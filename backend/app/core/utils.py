import uuid
from datetime import datetime, timezone

def utcnow():
    return datetime.now(timezone.utc)

def new_id():
    return str(uuid.uuid4())

def serialize_doc(doc):
    if doc is None:
        return None
    if isinstance(doc, list):
        return [serialize_doc(d) for d in doc]
    if isinstance(doc, dict):
        result = {}
        for k, v in doc.items():
            # We keep ObjectId as string if encountered,
            # but ideally we use our own IDs
            if k == "_id":
                continue
            if isinstance(v, datetime):
                result[k] = v.isoformat()
            elif isinstance(v, dict):
                result[k] = serialize_doc(v)
            elif isinstance(v, list):
                result[k] = [serialize_doc(i) if isinstance(i, (dict, list)) else i for i in v]
            else:
                result[k] = v
        return result
    return doc
