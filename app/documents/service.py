from typing import Optional

from fastapi import HTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session

from utils.log_function import log_function


@log_function
def get_document_total(db: Session):
    """Lấy thông tin tổng số văn bản từ bản ghi mới nhất"""
    query = text(
        """
        SELECT total_count, update_at
        FROM document_total
        ORDER BY update_at DESC
        LIMIT 1
        """
    )
    try:
        row = db.execute(query).fetchone()
        if not row:
            return {"total_count": 0, "update_at": None}
        return {"total_count": row[0], "update_at": row[1]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi document_total: {str(e)}")


@log_function
def get_document_status_report(db: Session):
    """Báo cáo số lượng văn bản phân loại theo trạng thái"""
    query = text(
        """
        SELECT
            status,
            COUNT(item_id) as total_count,
            MIN(updated_date) as oldest_update,
            MAX(updated_date) as latest_update
        FROM documents
        GROUP BY status
        ORDER BY total_count DESC
        """
    )
    try:
        result = db.execute(query).fetchall()
        return [
            {
                "status": row[0],
                "count": row[1],
                "oldest_update": row[2],
                "latest_update": row[3],
            }
            for row in result
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi document_info: {str(e)}")


@log_function
def get_recent_documents(db: Session, limit: int = 10):
    query = text(
        """
        SELECT ds.item_id, w.code, ds.end_time
        FROM document_state ds
        JOIN workflows w ON ds.workflow_id = w.id
        WHERE ds.end_time IS NOT NULL
        ORDER BY ds.end_time DESC
        LIMIT :limit
    """
    )
    try:
        result = db.execute(query, {"limit": limit}).fetchall()
        return [
            {"item_id": row[0], "step_code": row[1], "completed_at": row[2]}
            for row in result
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi recent_documents: {str(e)}")


@log_function
def get_issue_date_report(db: Session):
    """Thống kê số lượng văn bản theo năm ban hành"""
    query = text(
        """
        SELECT
            EXTRACT(YEAR FROM issue_date)::INTEGER as issue_year,
            COUNT(item_id) as total_count
        FROM documents
        WHERE issue_date IS NOT NULL
        GROUP BY issue_year
        ORDER BY issue_year DESC
    """
    )
    try:
        result = db.execute(query).fetchall()
        return [{"year": row[0], "count": row[1]} for row in result]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi issue_date_report: {str(e)}")


@log_function
def get_document_info_detail(
    db: Session, item_id: Optional[str] = None, document_number: Optional[str] = None
):
    """Lấy thông tin chi tiết của văn bản theo item_id hoặc document_number"""
    if not item_id and not document_number:
        raise HTTPException(
            status_code=400, detail="Vui lòng cung cấp item_id hoặc document_number"
        )

    conditions = []
    params = {}

    if item_id:
        conditions.append("item_id = :item_id")
        params["item_id"] = item_id
    if document_number:
        conditions.append("doc_num = :document_number")
        params["document_number"] = document_number

    where_clause = " OR ".join(conditions)

    query = text(
        f"""
        SELECT
            item_id, status, eff_from as effective_date, agency_name as issuing_agency,
            doc_num as document_number, issue_date, title, NULL as signer, NULL as position, updated_date as update_at
        FROM documents
        WHERE {where_clause}
        LIMIT 1
    """
    )

    try:
        row = db.execute(query, params).fetchone()
        if not row:
            raise HTTPException(
                status_code=404, detail="Không tìm thấy thông tin văn bản"
            )

        return {
            "item_id": row[0],
            "status": row[1],
            "effective_date": row[2],
            "issuing_agency": row[3],
            "document_number": row[4],
            "issue_date": row[5],
            "title": row[6],
            "signer": row[7],
            "position": row[8],
            "update_at": row[9],
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Lỗi khi lấy thông tin văn bản: {str(e)}"
        )


@log_function
def get_doc_types(db: Session):
    """Lấy danh sách loại văn bản cùng số lượng"""
    query = text(
        """
        SELECT dt.id, dt.code, dt.name, COUNT(d.item_id) as total_count
        FROM dim_doc_type dt
        LEFT JOIN documents d ON dt.id = d.doc_type_id
        GROUP BY dt.id, dt.code, dt.name
        ORDER BY dt.name ASC
        """
    )
    try:
        result = db.execute(query).fetchall()
        return [
            {"id": row[0], "code": row[1], "name": row[2], "total_count": row[3]}
            for row in result
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi dim_doc_type: {str(e)}")


@log_function
def get_eff_statuses(db: Session):
    """Lấy danh sách trạng thái hiệu lực cùng số lượng"""
    query = text(
        """
        SELECT es.id, es.code, es.name, COUNT(d.item_id) as total_count
        FROM dim_eff_status es
        LEFT JOIN documents d ON es.id = d.eff_status_id
        GROUP BY es.id, es.code, es.name
        ORDER BY es.name ASC
        """
    )
    try:
        result = db.execute(query).fetchall()
        return [
            {"id": row[0], "code": row[1], "name": row[2], "total_count": row[3]}
            for row in result
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi dim_eff_status: {str(e)}")


@log_function
def get_majors(db: Session):
    """Lấy danh sách lĩnh vực cùng số lượng"""
    query = text(
        """
        SELECT m.id, m.code, m.name, m.short_name, COUNT(dm.document_id) as total_count
        FROM dim_major m
        LEFT JOIN document_majors dm ON m.id = dm.major_id
        GROUP BY m.id, m.code, m.name, m.short_name
        ORDER BY m.name ASC
        """
    )
    try:
        result = db.execute(query).fetchall()
        return [
            {
                "id": row[0],
                "code": row[1],
                "name": row[2],
                "short_name": row[3],
                "total_count": row[4],
            }
            for row in result
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi dim_major: {str(e)}")
