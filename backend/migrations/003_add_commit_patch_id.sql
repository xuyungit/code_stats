-- UP
ALTER TABLE commits ADD COLUMN patch_id VARCHAR(40);
CREATE INDEX idx_commits_patch_id ON commits(patch_id);

-- DOWN
DROP INDEX idx_commits_patch_id;
ALTER TABLE commits DROP COLUMN patch_id;