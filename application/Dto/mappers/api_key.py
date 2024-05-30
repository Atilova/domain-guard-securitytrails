from typing import Optional

from application.Dto.api_key import (
    ApiKeyOutputDTO,
    ApiKeyCreationStatus,
    ApiKeyCredentials,
    ApiKeyCreationError
)

from domain.Entities.account import AccountObtainResult
from domain.Entities.orchestrator import OrchestratorResult
from domain.Entities.storage import JsonStorageRecord
from domain.Enums.account import ObtainResultCode
from domain.Enums.orchestrator import ProcessStatus


def map_get_api_key_to_dto(job_json: Optional[JsonStorageRecord]) -> ApiKeyOutputDTO:
    """map_get_api_key_to_dto"""

    output_dto = job_json is not None and ApiKeyOutputDTO.from_json(job_json.data.raw())
    if not output_dto:
        return ApiKeyOutputDTO(status=ApiKeyCreationStatus.NOT_FOUND)
    return output_dto

def _details_by_service_status(status: ObtainResultCode):
    """_details_by_status"""

    return {
        ObtainResultCode.UNDEFINED: 'Unexpected undefined state encountered.',
        ObtainResultCode.FAILED: 'Unexpected state or error encountered.',
        ObtainResultCode.TIMEOUTED: 'Job took too long to execute.'
    }.get(status)

def map_new_api_key_to_dto(result: OrchestratorResult, stored_dto: ApiKeyOutputDTO) -> ApiKeyOutputDTO:
    """_map_result_to_dto"""

    job_id = result.id.raw()
    job_status = result.status.raw()
    # Todo: use stored_dto to populate necessary fields
    populate_with = {}

    match job_status:
        case ProcessStatus.DONE:
            service_result: AccountObtainResult = result.result.raw()
            result_code = service_result.code.raw()
            match result_code:
                case ObtainResultCode.SUCCESS:
                    return ApiKeyOutputDTO(
                        id=job_id,
                        status=ApiKeyCreationStatus.READY,
                        data=ApiKeyCredentials(
                            email=service_result.email.raw(),
                            password=service_result.password.raw(),
                            api_key=service_result.api_key.raw()
                        ),
                        elapsed=result.elapsed.raw(),
                        **populate_with
                    )
                case _:
                    return ApiKeyOutputDTO(
                        id=job_id,
                        status=ApiKeyCreationStatus.REJECTED,
                        error=ApiKeyCreationError(details=_details_by_service_status(service_result)),
                        elapsed=result.elapsed.raw(),
                        **populate_with
                    )
        case ProcessStatus.FAILED:
            exception = result.exception.raw()
            return ApiKeyOutputDTO(
                id=job_id,
                status=ApiKeyCreationStatus.REJECTED,
                error=ApiKeyCreationError(details=f'Exception encountered while job processing: {exception}.'),
                elapsed=result.elapsed.raw(),
                **populate_with
            )
        case _:
            #Todo: Add logger
            return ApiKeyOutputDTO(
                id=job_id,
                status=ApiKeyCreationStatus.REJECTED,
                error=ApiKeyCreationError(details=f'Received unexpected orchestrator status: {job_status}.'),
                **populate_with
            )