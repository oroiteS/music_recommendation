<template>
    <div class="music-edit">
        <h2>编辑音乐信息</h2>
        <div v-if="music" class="edit-form">
            <div class="form-group">
                <label>标题</label>
                <input v-model="editedMusic.title" type="text" class="form-input">
            </div>

            <div class="form-group">
                <label>歌手</label>
                <input v-model="editedMusic.artist_name" type="text" class="form-input">
            </div>

            <div class="form-group">
                <label>流派</label>
                <input v-model="editedMusic.genre" type="text" class="form-input">
            </div>

            <div class="form-group">
                <label>封面图片</label>
                <div class="cover-upload">
                    <input type="file" @change="handleFileUpload" accept="image/*" ref="fileInput" class="file-input">
                    <button @click="$refs.fileInput.click()" class="upload-btn">
                        选择图片
                    </button>
                    <span class="file-name">{{ fileName || '未选择文件' }}</span>
                </div>
                <img :src="previewUrl || editedMusic.cover_url" class="cover-preview" alt="封面预览">
            </div>

            <div class="button-group">
                <button @click="saveChanges" class="save-btn">保存更改</button>
                <button @click="goBack" class="cancel-btn">取消</button>
            </div>
        </div>
    </div>
</template>

<script>
import axios from 'axios';

export default {
    data() {
        return {
            music: null,
            editedMusic: {
                title: '',
                artist_name: '',
                genre: '',
                cover_url: ''
            },
            isAdmin: false,
            previewUrl: null,
            fileName: '',
            newCoverUrl: null
        }
    },
    async created() {
        // 检查管理员权限
        const userInfo = sessionStorage.getItem('user');
        if (userInfo) {
            const user = JSON.parse(userInfo);
            this.isAdmin = user.user_identity === 1;
            if (!this.isAdmin) {
                this.$router.push('/');
                return;
            }
        }

        await this.loadMusicDetails();
    },
    methods: {
        async loadMusicDetails() {
            try {
                const musicId = this.$route.params.id;
                const response = await axios.get(`http://localhost:5000/music/${musicId}`);
                if (response.data.success) {
                    this.music = response.data.data;
                    // 复制数据到编辑表单
                    this.editedMusic = { ...this.music };
                }
            } catch (error) {
                console.error('加载音乐信息失败:', error);
            }
        },
        async handleFileUpload(event) {
            const file = event.target.files[0];
            if (!file) return;

            try {
                const formData = new FormData();
                formData.append('file', file);
                formData.append('artist_name', this.editedMusic.artist_name);
                formData.append('title', this.editedMusic.title);

                const response = await axios.post(
                    'http://localhost:5000/music/upload-cover',
                    formData,
                    {
                        headers: {
                            'Content-Type': 'multipart/form-data'
                        }
                    }
                );

                if (response.data.success) {
                    this.fileName = response.data.filename;
                    this.newCoverUrl = response.data.url;
                    this.previewUrl = URL.createObjectURL(file);
                    this.editedMusic.cover_url = response.data.url;
                    console.log('Upload response:', response.data);
                }
            } catch (error) {
                console.error('上传图片失败:', error);
                alert('上传图片失败，请重试');
            }
        },

        async saveChanges() {
            try {
                const musicId = this.$route.params.id;
                const updateData = {
                    ...this.editedMusic,
                    cover_url: this.newCoverUrl || this.editedMusic.cover_url
                };

                console.log('Sending update data:', updateData);

                const response = await axios.put(
                    `http://localhost:5000/music/${musicId}`, 
                    updateData
                );
                
                if (response.data.success) {
                    alert('更新成功！');
                    this.$router.push(`/music/${musicId}`);
                }
            } catch (error) {
                console.error('保存更改失败:', error);
                alert('保存失败，请重试');
            }
        },

        goBack() {
            this.$router.go(-1);
        }
    }
}
</script>

<style scoped>
.music-edit {
    max-width: 800px;
    margin: 0 auto;
    padding: 20px;
}

.edit-form {
    background-color: white;
    padding: 20px;
    border-radius: 8px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.form-group {
    margin-bottom: 20px;
}

.form-group label {
    display: block;
    margin-bottom: 8px;
    font-weight: bold;
}

.form-input {
    width: 100%;
    padding: 8px;
    border: 1px solid #ddd;
    border-radius: 4px;
}

.cover-preview {
    margin-top: 10px;
    max-width: 200px;
    border-radius: 4px;
}

.button-group {
    margin-top: 20px;
    display: flex;
    gap: 10px;
}

.save-btn,
.cancel-btn {
    padding: 10px 20px;
    border: none;
    border-radius: 4px;
    cursor: pointer;
}

.save-btn {
    background-color: #1db954;
    color: white;
}

.cancel-btn {
    background-color: #6c757d;
    color: white;
}

.cover-upload {
    display: flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 10px;
}

.file-input {
    display: none;
}

.upload-btn {
    padding: 8px 16px;
    background-color: #1db954;
    color: white;
    border: none;
    border-radius: 4px;
    cursor: pointer;
}

.file-name {
    color: #666;
    font-size: 0.9em;
}
</style>