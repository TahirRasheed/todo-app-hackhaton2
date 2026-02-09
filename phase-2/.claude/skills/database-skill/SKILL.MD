---
name: database-skill
description: Design databases, create tables, and manage migrations. Use for backend and data architecture tasks.
---

# Database Schema Design

## Instructions

1. **Table Creation**
   - Define primary keys for each table
   - Use appropriate data types
   - Add required constraints (NOT NULL, UNIQUE)
   - Follow consistent naming conventions

2. **Schema Design**
   - Identify entities and relationships
   - Normalize data (1NF, 2NF, 3NF)
   - Use foreign keys for relations
   - Avoid redundant data storage

3. **Migrations**
   - Create version-controlled migration files
   - Include up() and down() methods
   - Track schema changes over time
   - Never edit production tables directly

4. **Relationships**
   - One-to-One → user ↔ profile
   - One-to-Many → user ↔ tasks
   - Many-to-Many → users ↔ roles (pivot table)

---

## Best Practices

- Use UUID or auto-increment IDs
- Add timestamps (created_at, updated_at)
- Index frequently queried columns
- Use soft deletes where needed
- Keep tables focused on single responsibility
- Validate schema before deployment

---

## Example Structure

```sql
-- Users table
CREATE TABLE users (
  id SERIAL PRIMARY KEY,
  name VARCHAR(100) NOT NULL,
  email VARCHAR(150) UNIQUE NOT NULL,
  password TEXT NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tasks table
CREATE TABLE tasks (
  id SERIAL PRIMARY KEY,
  user_id INT REFERENCES users(id),
  title VARCHAR(200) NOT NULL,
  description TEXT,
  completed BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
