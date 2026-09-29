DROP TABLE IF EXISTS pending_upload;

CREATE TABLE pending_upload (
    path TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    normalized_title TEXT NOT NULL,
    extension TEXT
);

INSERT INTO pending_upload
SELECT
    l.path,
    l.title,
    l.normalized_title,
    l.extension
FROM local_books l
LEFT JOIN notion_books n
ON l.normalized_title = n.normalized_title
WHERE n.normalized_title IS NULL;
