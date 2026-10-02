

-- 1. Users Table
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    telegram_id BIGINT NOT NULL UNIQUE,
    full_name VARCHAR(255) NOT NULL,
    username VARCHAR(255) NULL,
    language VARCHAR(10) NOT NULL DEFAULT 'en',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_telegram_id (telegram_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 2. Courses Table
CREATE TABLE IF NOT EXISTS courses (
    id VARCHAR(50) PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    price VARCHAR(50) NOT NULL,
    telebirr_number VARCHAR(50) NOT NULL,
    cbe_number VARCHAR(50) NOT NULL,
    description TEXT,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 3. Payments Table (Each payment has its own unique ID)
CREATE TABLE IF NOT EXISTS payments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    course_id VARCHAR(50) NOT NULL,
    file_type ENUM('photo', 'document') NOT NULL,
    file_id VARCHAR(255) NOT NULL,
    status ENUM('pending', 'approved', 'rejected') NOT NULL DEFAULT 'pending',
    submission_count INT NOT NULL DEFAULT 1,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    approved_at DATETIME NULL,
    rejected_at DATETIME NULL,
    INDEX idx_payments_status (status),
    INDEX idx_payments_user (user_id),
    CONSTRAINT fk_payments_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    CONSTRAINT fk_payments_course FOREIGN KEY (course_id) REFERENCES courses(id) ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 4. Enrollments Table
CREATE TABLE IF NOT EXISTS enrollments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    course_id VARCHAR(50) NOT NULL,
    payment_id INT NOT NULL,
    status ENUM('active', 'expired', 'revoked') NOT NULL DEFAULT 'active',
    invite_link VARCHAR(255) NULL,
    enrolled_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_enrollments_user (user_id),
    INDEX idx_enrollments_course (course_id),
    CONSTRAINT fk_enrollments_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    CONSTRAINT fk_enrollments_course FOREIGN KEY (course_id) REFERENCES courses(id) ON DELETE RESTRICT,
    CONSTRAINT fk_enrollments_payment FOREIGN KEY (payment_id) REFERENCES payments(id) ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Initial Course Data: Freshman Course
INSERT INTO courses (id, title, price, telebirr_number, cbe_number, description)
VALUES (
    'freshman',
    'Freshman Courses (English, Mathematics, Logic, Psychology, Economics, Entrepreneurship, Physics, Anthropology, History, Computer Programming, Physical Fitness...)',
    '400 ETB',
    '0929781996',
    '1000316427735',
    'PDFs + Videos Lessons + Past years Mid and final Exams, Department info and More'
)
ON DUPLICATE KEY UPDATE
    title = VALUES(title),
    price = VALUES(price),
    telebirr_number = VALUES(telebirr_number),
    cbe_number = VALUES(cbe_number),
    description = VALUES(description);
