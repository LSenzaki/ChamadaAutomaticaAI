-- =====================================================
-- DATABASE SCHEMA FOR FACIAL RECOGNITION ATTENDANCE SYSTEM
-- Supabase (PostgreSQL)
-- =====================================================

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- =====================================================
-- TABLE: turmas (Classes)
-- =====================================================
CREATE TABLE IF NOT EXISTS turmas (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(255) NOT NULL UNIQUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_turmas_nome ON turmas(nome);

COMMENT ON TABLE turmas IS 'Classes/turmas where students are enrolled';
COMMENT ON COLUMN turmas.nome IS 'Class name (e.g., "IA 1º Ano", "Data Science 3º Ano")';

-- =====================================================
-- TABLE: professores (Professors)
-- =====================================================
CREATE TABLE IF NOT EXISTS professores (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    ativo BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_professores_email ON professores(email);
CREATE INDEX idx_professores_ativo ON professores(ativo);

COMMENT ON TABLE professores IS 'Professors who validate attendances';
COMMENT ON COLUMN professores.email IS 'Professor email address (unique)';
COMMENT ON COLUMN professores.ativo IS 'Whether professor account is active';

-- =====================================================
-- TABLE: turmas_professores (Many-to-Many Relationship)
-- =====================================================
CREATE TABLE IF NOT EXISTS turmas_professores (
    id SERIAL PRIMARY KEY,
    turma_id INTEGER NOT NULL REFERENCES turmas(id) ON DELETE CASCADE,
    professor_id INTEGER NOT NULL REFERENCES professores(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(turma_id, professor_id)
);

CREATE INDEX idx_turmas_professores_turma ON turmas_professores(turma_id);
CREATE INDEX idx_turmas_professores_professor ON turmas_professores(professor_id);

COMMENT ON TABLE turmas_professores IS 'Assignment of professors to classes (many-to-many)';

-- =====================================================
-- TABLE: alunos (Students)
-- =====================================================
CREATE TABLE IF NOT EXISTS alunos (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(255) NOT NULL,
    turma_id INTEGER REFERENCES turmas(id) ON DELETE SET NULL,
    check_professor BOOLEAN DEFAULT FALSE,
    ativo BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_alunos_nome ON alunos(nome);
CREATE INDEX idx_alunos_turma ON alunos(turma_id);
CREATE INDEX idx_alunos_check_professor ON alunos(check_professor);
CREATE INDEX idx_alunos_ativo ON alunos(ativo);

COMMENT ON TABLE alunos IS 'Students enrolled in the system';
COMMENT ON COLUMN alunos.check_professor IS 'Whether student registration is validated by professor';
COMMENT ON COLUMN alunos.ativo IS 'Whether student account is active';

-- =====================================================
-- TABLE: face_embeddings (Face Recognition Data)
-- =====================================================
CREATE TABLE IF NOT EXISTS face_embeddings (
    id SERIAL PRIMARY KEY,
    aluno_id INTEGER NOT NULL REFERENCES alunos(id) ON DELETE CASCADE,
    embedding BYTEA NOT NULL,
    foto_nome VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_face_embeddings_aluno ON face_embeddings(aluno_id);

COMMENT ON TABLE face_embeddings IS 'Face embedding vectors for facial recognition';
COMMENT ON COLUMN face_embeddings.embedding IS 'Serialized face embedding vector (128-dim or 512-dim)';
COMMENT ON COLUMN face_embeddings.foto_nome IS 'Original photo filename for reference';

-- =====================================================
-- TABLE: presencas (Attendances)
-- =====================================================
CREATE TABLE IF NOT EXISTS presencas (
    id SERIAL PRIMARY KEY,
    aluno_id INTEGER NOT NULL REFERENCES alunos(id) ON DELETE CASCADE,
    turma_id INTEGER REFERENCES turmas(id) ON DELETE SET NULL,
    data_hora TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    confianca NUMERIC(5,2) CHECK (confianca >= 0 AND confianca <= 100),
    check_professor BOOLEAN DEFAULT FALSE,
    validado_em TIMESTAMP WITH TIME ZONE,
    validado_por INTEGER REFERENCES professores(id) ON DELETE SET NULL,
    observacao TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_presencas_aluno ON presencas(aluno_id);
CREATE INDEX idx_presencas_turma ON presencas(turma_id);
CREATE INDEX idx_presencas_data ON presencas(data_hora);
CREATE INDEX idx_presencas_check_professor ON presencas(check_professor);
CREATE INDEX idx_presencas_data_aluno ON presencas(data_hora, aluno_id);

COMMENT ON TABLE presencas IS 'Attendance records from facial recognition';
COMMENT ON COLUMN presencas.confianca IS 'Confidence percentage from facial recognition (0-100)';
COMMENT ON COLUMN presencas.check_professor IS 'Whether attendance is validated by professor';
COMMENT ON COLUMN presencas.validado_por IS 'Professor who validated the attendance';
COMMENT ON COLUMN presencas.observacao IS 'Optional notes from professor';

-- =====================================================
-- TRIGGERS: Update updated_at timestamp
-- =====================================================

-- Function to update updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Trigger for turmas
CREATE TRIGGER update_turmas_updated_at BEFORE UPDATE ON turmas
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Trigger for professores
CREATE TRIGGER update_professores_updated_at BEFORE UPDATE ON professores
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Trigger for alunos
CREATE TRIGGER update_alunos_updated_at BEFORE UPDATE ON alunos
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- =====================================================
-- VIEWS: Useful queries for common operations
-- =====================================================

-- View: Students with class information
CREATE OR REPLACE VIEW vw_alunos_completo AS
SELECT 
    a.id,
    a.nome,
    a.turma_id,
    t.nome as turma_nome,
    a.check_professor,
    a.ativo,
    COUNT(DISTINCT fe.id) as num_fotos,
    a.created_at,
    a.updated_at
FROM alunos a
LEFT JOIN turmas t ON a.turma_id = t.id
LEFT JOIN face_embeddings fe ON a.id = fe.aluno_id
GROUP BY a.id, t.nome;

COMMENT ON VIEW vw_alunos_completo IS 'Complete student information with class and photo count';

-- View: Professors with assigned classes
CREATE OR REPLACE VIEW vw_professores_turmas AS
SELECT 
    p.id as professor_id,
    p.nome as professor_nome,
    p.email,
    p.ativo,
    json_agg(
        json_build_object(
            'id', t.id,
            'nome', t.nome
        ) ORDER BY t.nome
    ) FILTER (WHERE t.id IS NOT NULL) as turmas
FROM professores p
LEFT JOIN turmas_professores tp ON p.id = tp.professor_id
LEFT JOIN turmas t ON tp.turma_id = t.id
GROUP BY p.id;

COMMENT ON VIEW vw_professores_turmas IS 'Professors with their assigned classes as JSON array';

-- View: Attendances with complete information
CREATE OR REPLACE VIEW vw_presencas_completo AS
SELECT 
    pr.id,
    pr.aluno_id,
    a.nome as aluno_nome,
    pr.turma_id,
    t.nome as turma_nome,
    pr.data_hora,
    pr.confianca,
    pr.check_professor,
    pr.validado_em,
    pr.validado_por,
    prof.nome as professor_nome,
    pr.observacao,
    DATE(pr.data_hora) as data,
    pr.created_at
FROM presencas pr
INNER JOIN alunos a ON pr.aluno_id = a.id
LEFT JOIN turmas t ON pr.turma_id = t.id
LEFT JOIN professores prof ON pr.validado_por = prof.id;

COMMENT ON VIEW vw_presencas_completo IS 'Complete attendance information with student, class and professor names';

-- =====================================================
-- FUNCTIONS: Useful stored procedures
-- =====================================================

-- Function: Get attendances by date
CREATE OR REPLACE FUNCTION get_presencas_by_date(data_consulta DATE)
RETURNS TABLE (
    id INTEGER,
    aluno_id INTEGER,
    aluno_nome VARCHAR,
    turma_id INTEGER,
    turma_nome VARCHAR,
    professor_nome VARCHAR,
    data_hora TIMESTAMP WITH TIME ZONE,
    confianca NUMERIC,
    check_professor BOOLEAN
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        pr.id,
        pr.aluno_id,
        a.nome,
        pr.turma_id,
        t.nome,
        prof.nome,
        pr.data_hora,
        pr.confianca,
        pr.check_professor
    FROM presencas pr
    INNER JOIN alunos a ON pr.aluno_id = a.id
    LEFT JOIN turmas t ON pr.turma_id = t.id
    LEFT JOIN turmas_professores tp ON t.id = tp.turma_id
    LEFT JOIN professores prof ON tp.professor_id = prof.id
    WHERE DATE(pr.data_hora) = data_consulta
    ORDER BY pr.data_hora DESC;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION get_presencas_by_date IS 'Retrieve all attendances for a specific date';

-- =====================================================
-- SAMPLE DATA (Optional - for testing)
-- =====================================================

-- Insert sample classes
INSERT INTO turmas (nome) VALUES 
    ('IA 1º Ano'),
    ('Data Science 3º Ano'),
    ('Machine Learning 2º Ano')
ON CONFLICT (nome) DO NOTHING;

-- Insert sample professor
INSERT INTO professores (nome, email) VALUES 
    ('Prof. Maria Santos', 'maria.santos@escola.com'),
    ('Prof. João Silva', 'joao.silva@escola.com')
ON CONFLICT (email) DO NOTHING;

-- Assign professors to classes
INSERT INTO turmas_professores (turma_id, professor_id)
SELECT t.id, p.id
FROM turmas t, professores p
WHERE t.nome = 'IA 1º Ano' AND p.email = 'maria.santos@escola.com'
ON CONFLICT DO NOTHING;

-- =====================================================
-- SECURITY: Row Level Security (RLS) - Optional
-- =====================================================
-- Uncomment if you want to add authentication later

-- ALTER TABLE alunos ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE professores ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE turmas ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE presencas ENABLE ROW LEVEL SECURITY;

-- Example policy: Professors can only see their own classes
-- CREATE POLICY professor_turmas_policy ON turmas
--     FOR SELECT
--     USING (
--         id IN (
--             SELECT turma_id FROM turmas_professores
--             WHERE professor_id = current_setting('app.current_professor_id')::INTEGER
--         )
--     );

-- =====================================================
-- CLEANUP SCRIPT (Use with caution - drops all tables)
-- =====================================================
/*
DROP VIEW IF EXISTS vw_presencas_completo CASCADE;
DROP VIEW IF EXISTS vw_professores_turmas CASCADE;
DROP VIEW IF EXISTS vw_alunos_completo CASCADE;
DROP FUNCTION IF EXISTS get_presencas_by_date CASCADE;
DROP FUNCTION IF EXISTS update_updated_at_column CASCADE;
DROP TABLE IF EXISTS presencas CASCADE;
DROP TABLE IF EXISTS face_embeddings CASCADE;
DROP TABLE IF EXISTS turmas_professores CASCADE;
DROP TABLE IF EXISTS alunos CASCADE;
DROP TABLE IF EXISTS professores CASCADE;
DROP TABLE IF EXISTS turmas CASCADE;
*/

-- =====================================================
-- END OF SCHEMA
-- =====================================================
