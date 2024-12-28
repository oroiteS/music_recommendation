create database python_final;
use python_final;
CREATE TABLE users (
    userid VARCHAR(255) PRIMARY KEY,         -- 用户ID（登录用）
    username NVARCHAR(255) NOT NULL,         -- 用户名（显示用，可修改）
    login_id VARCHAR(255) NOT NULL UNIQUE,   -- 登录账号（不可修改）
    password VARCHAR(255) NOT NULL,          -- 密码
    user_identity INT DEFAULT 0              -- 用户身份（0普通用户，1管理员）
);

-- 创建音乐表
CREATE TABLE music (
    id INT IDENTITY(1,1) PRIMARY KEY,                                     -- 自动增长的主键
    title nVARCHAR(255) NOT NULL,                                         -- 歌曲名称
    artist_name nVARCHAR(255) NOT NULL,                                   -- 歌手名称
    genre nVARCHAR(255),                                                  -- 音乐类型（可以存储多个类型）
    play_count INT DEFAULT 0,                                             -- 播放次数，默认值为0
    cover_url nVARCHAR(255) DEFAULT '/static/music_img/default_cover.jpg' -- 专辑封面默认地址
);

-- 创建歌单表
CREATE TABLE playlists (
    id          INT IDENTITY(1,1) PRIMARY KEY, -- 自动增长的主键
    userid      varchar(255) NOT NULL,         -- 用户ID
    title       nVARCHAR(255) NOT NULL,         -- 歌单名称
    description nvarchar(max),                  -- 歌单描述
    created_at  DATETIME DEFAULT GETDATE(),    -- 创建时间，默认当前时间
);

-- 创建歌单-歌曲表
CREATE TABLE playlist_songs (
    playlist_id INT NOT NULL,            -- 歌单ID
    music_id INT NOT NULL,               -- 歌曲ID
    PRIMARY KEY (playlist_id, music_id)  -- 复合主键
);

-- 创建评论表
CREATE TABLE comments (
    id           INT IDENTITY(1,1) PRIMARY KEY, -- 自动增长的主键
    userid       varchar(255) NOT NULL,         -- 用户ID
    music_id     INT NOT NULL,                  -- 歌曲ID
    comment_text nvarchar(max),                  -- 评论内容
    created_at   DATETIME DEFAULT GETDATE(),    -- 评论时间，默认当前时间
);

-- 创建评分表
CREATE TABLE ratings (
    id INT IDENTITY(1,1) PRIMARY KEY,   -- 自动增长的主键
    userid varchar(255) NOT NULL,       -- 用户ID
    music_id INT NOT NULL,               -- 歌曲ID
    rating_value INT CHECK (rating_value BETWEEN 1 AND 5), -- 评分值，范围为1到5
);

-- 创建播放历史表
CREATE TABLE user_play_history (
    id INT IDENTITY(1,1) PRIMARY KEY,   -- 自动增长的主键
    userid nvarchar(255) NOT NULL,       -- 用户ID
    music_id INT NOT NULL,               -- 歌曲ID
    played_at DATETIME DEFAULT GETDATE(), -- 播放时间，默认当前时间
);

-- 用户偏好表
CREATE TABLE user_preferences
(
    id               INT IDENTITY (1,1) PRIMARY KEY,
    userid           VARCHAR(255) NOT NULL,
    favorite_genres  NVARCHAR(255), -- 喜欢的音乐类型（用逗号分隔的字符串）
    favorite_artists NVARCHAR(255), -- 喜欢的艺术家（用逗号分隔的字符串）
    listening_times  NVARCHAR(255)  -- 常听时段（用逗号分隔的字符串）
);
