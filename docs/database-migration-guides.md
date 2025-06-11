# Database Migration Guides

## Migration SQL

backend/migrations

## Best Practices (IMPORTANT - Follow these to avoid migration failures)

1. **Order of Operations**: ALWAYS follow this sequence:
   - Create migration file FIRST
   - Apply migration to update database schema
   - THEN update SQLAlchemy models to match
   - Never update models before running migrations
   
2. **Migration File Format**:
   - Use simple format: `{version}_{description}.sql` (e.g., `003_add_commit_patch_id.sql`)
   - Keep SQL statements clean and simple
   - Start with `-- UP` and `-- DOWN` markers only
   - Avoid complex comments that might confuse the parser
   
3. **Migration Content Structure**:
   ```sql
   -- UP
   ALTER TABLE commits ADD COLUMN patch_id VARCHAR(40);
   CREATE INDEX idx_commits_patch_id ON commits(patch_id);
   
   -- DOWN
   DROP INDEX idx_commits_patch_id;
   ALTER TABLE commits DROP COLUMN patch_id;
   ```

4. **Testing and Verification**:
   - Test migrations on a copy of the database first
   - Verify schema changes with: `sqlite3 git_stats.db ".schema table_name"`
   - Check migration status: `mm.get_applied_migrations()`
   
5. **Handling Migration Failures**:
   - If a migration fails due to "column already exists", check if models were updated first
   - Manually verify database state before proceeding
   - May need to manually record migration as applied if schema already matches

6. **Common Pitfalls to Avoid**:
   - Don't update models before migrations
   - Don't include descriptive comments in the SQL section
   - Don't assume migrations will auto-retry on failure
   - Always check for existing schema before adding columns