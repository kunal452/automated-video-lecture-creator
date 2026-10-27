-- ==============================================================================
-- DATABASE SCHEMA: Automated Video Lecture Creator System
-- Target DBMS: PostgreSQL 14+
-- Purpose: Final Year Project Report & Production Metadata Store
-- ==============================================================================

-- Enable UUID extension for globally unique entity IDs
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 1. Users Table
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    full_name VARCHAR(100),
    role VARCHAR(50) DEFAULT 'student' CHECK (role IN ('student', 'instructor', 'admin')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 2. Projects (Lecture Decks)
CREATE TABLE projects (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    source_type VARCHAR(50) NOT NULL CHECK (source_type IN ('pdf', 'pptx', 'markdown', 'topic_prompt', 'manual')),
    source_file_url TEXT,
    aspect_ratio VARCHAR(10) DEFAULT '16:9',
    voice_profile VARCHAR(100) DEFAULT 'en-US-ChristopherNeural',
    theme VARCHAR(50) DEFAULT 'dark_modern',
    status VARCHAR(50) DEFAULT 'draft' CHECK (status IN ('draft', 'processing', 'completed', 'failed')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 3. Individual Slides
CREATE TABLE slides (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    slide_index INT NOT NULL,
    slide_title VARCHAR(255) NOT NULL,
    extracted_text TEXT,
    bullet_points JSONB DEFAULT '[]'::jsonb,
    code_snippet TEXT,
    generated_script TEXT NOT NULL,
    image_url TEXT,
    duration_seconds NUMERIC(6, 2) DEFAULT 0.00,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT unique_project_slide_index UNIQUE (project_id, slide_index)
);

-- 4. Audio Tracks per Slide
CREATE TABLE audio_tracks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    slide_id UUID UNIQUE NOT NULL REFERENCES slides(id) ON DELETE CASCADE,
    audio_file_url TEXT NOT NULL,
    format VARCHAR(10) DEFAULT 'mp3',
    duration_seconds NUMERIC(6, 2) NOT NULL,
    timestamps_json JSONB, -- Stores word-level / sentence timing: [{"word": "Hello", "start": 0.0, "end": 0.4}]
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 5. Video Renders (Final Deliverables)
CREATE TABLE video_renders (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    resolution VARCHAR(20) DEFAULT '1920x1080',
    output_video_url TEXT,
    subtitle_srt_url TEXT,
    subtitle_vtt_url TEXT,
    total_duration_seconds NUMERIC(8, 2),
    file_size_bytes BIGINT,
    render_status VARCHAR(50) DEFAULT 'queued' CHECK (render_status IN ('queued', 'synthesizing', 'rendering', 'ready', 'failed')),
    error_message TEXT,
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for high-throughput query performance
CREATE INDEX idx_projects_user_id ON projects(user_id);
CREATE INDEX idx_slides_project_id ON slides(project_id);
CREATE INDEX idx_audio_tracks_slide_id ON audio_tracks(slide_id);
CREATE INDEX idx_video_renders_project_id ON video_renders(project_id);
