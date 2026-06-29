from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, BackgroundTasks, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse, PlainTextResponse, Response

from app.core.errors import UserFacingError
from app.services.analysis_service import (
    create_analysis,
    delete_analysis,
    export_csv,
    export_json,
    get_analysis,
    run_analysis,
    video_file_path,
)

router = APIRouter(prefix="/api/analyses", tags=["analyses"])


@router.post("")
async def post_analysis(
    background_tasks: BackgroundTasks,
    video: Annotated[UploadFile, File()],
    subtitle: Annotated[UploadFile | None, File()] = None,
    language: Annotated[str | None, Form()] = None,
    silenceThresholdDb: Annotated[float | None, Form()] = None,
    minSilenceDuration: Annotated[float | None, Form()] = None,
    longSceneSeconds: Annotated[float | None, Form()] = None,
):
    try:
        created, video_path, subtitle_path = await create_analysis(video, subtitle)
        background_tasks.add_task(
            run_analysis,
            created.analysisId,
            video_path,
            subtitle_path,
            language,
            silenceThresholdDb,
            minSilenceDuration,
            longSceneSeconds,
        )
        return created
    except UserFacingError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.message) from exc


@router.get("/{analysis_id}")
def get_analysis_route(analysis_id: str):
    try:
        return get_analysis(analysis_id)
    except UserFacingError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.message) from exc


@router.get("/{analysis_id}/video")
def get_video_route(analysis_id: str):
    try:
        return FileResponse(video_file_path(analysis_id), media_type="video/mp4")
    except UserFacingError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.message) from exc


@router.get("/{analysis_id}/export/json")
def get_json_route(analysis_id: str):
    try:
        return Response(
            content=export_json(analysis_id),
            media_type="application/json",
            headers={"Content-Disposition": f'attachment; filename="{analysis_id}.json"'},
        )
    except UserFacingError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.message) from exc


@router.get("/{analysis_id}/export/csv")
def get_csv_route(analysis_id: str):
    try:
        return PlainTextResponse(
            export_csv(analysis_id),
            media_type="text/csv",
            headers={"Content-Disposition": f'attachment; filename="{analysis_id}.csv"'},
        )
    except UserFacingError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.message) from exc


@router.delete("/{analysis_id}")
def delete_analysis_route(analysis_id: str):
    try:
        deleted = delete_analysis(analysis_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="분석 결과를 찾을 수 없습니다.")
        return {"deleted": True}
    except UserFacingError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.message) from exc
