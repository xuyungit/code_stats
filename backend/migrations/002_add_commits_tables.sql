-- UP
-- Add commits and commit co-authors tables for detailed commit tracking

-- Commits table (individual git commits)
CREATE TABLE IF NOT EXISTS commits (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    repository_id INTEGER NOT NULL,
    author_id INTEGER NOT NULL,
    hash VARCHAR(40) NOT NULL,
    message TEXT NOT NULL,
    commit_datetime TIMESTAMP NOT NULL,
    added_lines INTEGER DEFAULT 0,
    deleted_lines INTEGER DEFAULT 0,
    files_changed INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (repository_id) REFERENCES repositories(id) ON DELETE CASCADE,
    FOREIGN KEY (author_id) REFERENCES authors(id) ON DELETE CASCADE,
    UNIQUE(repository_id, hash)
);

-- Commit co-authors junction table
CREATE TABLE IF NOT EXISTS commit_co_authors (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    commit_id INTEGER NOT NULL,
    author_id INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (commit_id) REFERENCES commits(id) ON DELETE CASCADE,
    FOREIGN KEY (author_id) REFERENCES authors(id) ON DELETE CASCADE,
    UNIQUE(commit_id, author_id)
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_commits_repo_date ON commits(repository_id, commit_datetime);
CREATE INDEX IF NOT EXISTS idx_commits_author_date ON commits(author_id, commit_datetime);
CREATE INDEX IF NOT EXISTS idx_commits_hash ON commits(hash);
CREATE INDEX IF NOT EXISTS idx_commit_co_authors_commit ON commit_co_authors(commit_id);
CREATE INDEX IF NOT EXISTS idx_commit_co_authors_author ON commit_co_authors(author_id);

-- DOWN
DROP INDEX IF EXISTS idx_commit_co_authors_author;
DROP INDEX IF EXISTS idx_commit_co_authors_commit;
DROP INDEX IF EXISTS idx_commits_hash;
DROP INDEX IF EXISTS idx_commits_author_date;
DROP INDEX IF EXISTS idx_commits_repo_date;
DROP TABLE IF EXISTS commit_co_authors;
DROP TABLE IF EXISTS commits;