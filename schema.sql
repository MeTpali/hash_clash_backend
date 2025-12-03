-- ============================================================
-- Схема базы данных для Hash Clash
-- ============================================================
-- Этот файл содержит SQL запросы для создания схемы БД
-- в соответствии с моделями SQLAlchemy проекта
-- ============================================================

-- Создание схемы
CREATE SCHEMA IF NOT EXISTS cybersecurity_lab;

-- Установка схемы по умолчанию (опционально, можно убрать, так как все таблицы создаются с явным указанием схемы)
-- SET search_path TO cybersecurity_lab, public;

-- ============================================================
-- Таблица users (Пользователи)
-- ============================================================
CREATE TABLE IF NOT EXISTS cybersecurity_lab.users (
    id SERIAL PRIMARY KEY,
    username VARCHAR NOT NULL UNIQUE,
    email VARCHAR UNIQUE,
    user_type VARCHAR NOT NULL,
    password_hash VARCHAR NOT NULL,
    is_email_confirmed BOOLEAN NOT NULL DEFAULT FALSE,
    totp_key VARCHAR,
    is_totp_confirmed BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN NOT NULL DEFAULT TRUE
);

-- Индекс на id (создается автоматически для PRIMARY KEY)
-- Примечание: индексы на username и email создаются автоматически благодаря UNIQUE ограничениям
-- Дополнительные индексы ниже создаются для оптимизации запросов с условиями

-- Индекс на email для быстрого поиска по email (уникальный индекс уже создан автоматически, но частичный индекс для NULL значений может быть полезен)
CREATE INDEX IF NOT EXISTS idx_users_email ON cybersecurity_lab.users(email) WHERE email IS NOT NULL;

-- ============================================================
-- Таблица texts (Тексты)
-- ============================================================
CREATE TABLE IF NOT EXISTS cybersecurity_lab.texts (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    encryption_type VARCHAR NOT NULL,
    text VARCHAR NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    CONSTRAINT fk_texts_user_id 
        FOREIGN KEY (user_id) 
        REFERENCES cybersecurity_lab.users(id) 
        ON DELETE CASCADE
);

-- Индекс на id (создается автоматически для PRIMARY KEY)
-- Индекс на user_id для быстрого поиска текстов пользователя
CREATE INDEX IF NOT EXISTS idx_texts_user_id ON cybersecurity_lab.texts(user_id);

-- Индекс на encryption_type для фильтрации по типу шифрования
CREATE INDEX IF NOT EXISTS idx_texts_encryption_type ON cybersecurity_lab.texts(encryption_type);

-- Индекс на created_at для сортировки по дате создания
CREATE INDEX IF NOT EXISTS idx_texts_created_at ON cybersecurity_lab.texts(created_at DESC);

-- Составной индекс для быстрого поиска активных текстов пользователя
CREATE INDEX IF NOT EXISTS idx_texts_user_active ON cybersecurity_lab.texts(user_id, is_active) 
    WHERE is_active = TRUE;

-- ============================================================
-- Таблица temp_codes (Временные коды)
-- ============================================================
CREATE TABLE IF NOT EXISTS cybersecurity_lab.temp_codes (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    code VARCHAR(6) NOT NULL,
    code_type VARCHAR(50) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP NOT NULL,
    is_used BOOLEAN NOT NULL DEFAULT FALSE,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    CONSTRAINT fk_temp_codes_user_id 
        FOREIGN KEY (user_id) 
        REFERENCES cybersecurity_lab.users(id) 
        ON DELETE CASCADE
);

-- Индекс на id (создается автоматически для PRIMARY KEY)
-- Индекс на user_id для быстрого поиска кодов пользователя
CREATE INDEX IF NOT EXISTS idx_temp_codes_user_id ON cybersecurity_lab.temp_codes(user_id);

-- Индекс на code для быстрого поиска кода
CREATE INDEX IF NOT EXISTS idx_temp_codes_code ON cybersecurity_lab.temp_codes(code);

-- Индекс на code_type для фильтрации по типу кода
CREATE INDEX IF NOT EXISTS idx_temp_codes_code_type ON cybersecurity_lab.temp_codes(code_type);

-- Индекс на expires_at для поиска неистекших кодов
CREATE INDEX IF NOT EXISTS idx_temp_codes_expires_at ON cybersecurity_lab.temp_codes(expires_at);

-- Составной индекс для быстрого поиска активных неиспользованных кодов
CREATE INDEX IF NOT EXISTS idx_temp_codes_active_unused ON cybersecurity_lab.temp_codes(user_id, is_active, is_used) 
    WHERE is_active = TRUE AND is_used = FALSE;

-- ============================================================
-- Комментарии к таблицам и полям
-- ============================================================

COMMENT ON SCHEMA cybersecurity_lab IS 'Схема базы данных для приложения Hash Clash';

COMMENT ON TABLE cybersecurity_lab.users IS 'Таблица пользователей системы';
COMMENT ON COLUMN cybersecurity_lab.users.id IS 'Уникальный идентификатор пользователя';
COMMENT ON COLUMN cybersecurity_lab.users.username IS 'Имя пользователя (логин), уникальное';
COMMENT ON COLUMN cybersecurity_lab.users.email IS 'Email пользователя, уникальный, опциональный';
COMMENT ON COLUMN cybersecurity_lab.users.user_type IS 'Тип пользователя (user, admin)';
COMMENT ON COLUMN cybersecurity_lab.users.password_hash IS 'Хеш пароля пользователя';
COMMENT ON COLUMN cybersecurity_lab.users.is_email_confirmed IS 'Подтвержден ли email пользователя';
COMMENT ON COLUMN cybersecurity_lab.users.totp_key IS 'Ключ для двухфакторной аутентификации (TOTP)';
COMMENT ON COLUMN cybersecurity_lab.users.is_totp_confirmed IS 'Подтверждена ли двухфакторная аутентификация';
COMMENT ON COLUMN cybersecurity_lab.users.created_at IS 'Дата и время создания учетной записи';
COMMENT ON COLUMN cybersecurity_lab.users.is_active IS 'Активен ли пользователь';

COMMENT ON TABLE cybersecurity_lab.texts IS 'Таблица зашифрованных текстов пользователей';
COMMENT ON COLUMN cybersecurity_lab.texts.id IS 'Уникальный идентификатор текста';
COMMENT ON COLUMN cybersecurity_lab.texts.user_id IS 'Идентификатор пользователя-владельца текста';
COMMENT ON COLUMN cybersecurity_lab.texts.encryption_type IS 'Тип шифрования (rsa, grasshopper)';
COMMENT ON COLUMN cybersecurity_lab.texts.text IS 'Зашифрованный текст';
COMMENT ON COLUMN cybersecurity_lab.texts.created_at IS 'Дата и время создания текста';
COMMENT ON COLUMN cybersecurity_lab.texts.is_active IS 'Активен ли текст (используется для мягкого удаления)';

COMMENT ON TABLE cybersecurity_lab.temp_codes IS 'Таблица временных кодов для подтверждения email и других операций';
COMMENT ON COLUMN cybersecurity_lab.temp_codes.id IS 'Уникальный идентификатор кода';
COMMENT ON COLUMN cybersecurity_lab.temp_codes.user_id IS 'Идентификатор пользователя, для которого создан код';
COMMENT ON COLUMN cybersecurity_lab.temp_codes.code IS 'Временный код (6 символов)';
COMMENT ON COLUMN cybersecurity_lab.temp_codes.code_type IS 'Тип кода (email_confirmation, login_confirmation, etc.)';
COMMENT ON COLUMN cybersecurity_lab.temp_codes.created_at IS 'Дата и время создания кода';
COMMENT ON COLUMN cybersecurity_lab.temp_codes.expires_at IS 'Дата и время истечения кода';
COMMENT ON COLUMN cybersecurity_lab.temp_codes.is_used IS 'Использован ли код';
COMMENT ON COLUMN cybersecurity_lab.temp_codes.is_active IS 'Активен ли код';

-- ============================================================
-- Конец скрипта
-- ============================================================

