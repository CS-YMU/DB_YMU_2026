erDiagram
    Students {
        VARCHAR(20) student_id PK
        VARCHAR(50) name
        ENUM gender
        INT age
        VARCHAR(100) major
        VARCHAR(20) phone
        TIMESTAMP created_at
        TIMESTAMP updated_at
    }

    Teacher {
        VARCHAR(20) teacher_id PK
        VARCHAR(50) name
        ENUM gender
        INT age
        VARCHAR(20) title
        VARCHAR(20) phone
        TIMESTAMP created_at
        TIMESTAMP updated_at
    }

    Course {
        VARCHAR(20) course_id PK
        VARCHAR(100) course_name
        VARCHAR(20) teacher_id FK
        DECIMAL credit
        TIMESTAMP created_at
    }

    SC {
        INT id PK
        VARCHAR(20) student_id FK
        VARCHAR(20) course_id FK
        VARCHAR(20) semester
        DECIMAL score
        TIMESTAMP created_at
    }

    Students ||--o{ SC : "选修"
    Course ||--o{ SC : "被选"
    Teacher ||--o{ Course : "讲授"