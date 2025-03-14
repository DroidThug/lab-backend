import apiClient from './client';

export interface LoginResponse {
    message: string;
    token: string;
    role: string;
}

export const auth = {
    async login(username: string, password: string): Promise<LoginResponse> {
        const response = await apiClient.post<LoginResponse>('/api/auth/login/', { username, password });
        if (response.data.token) {
            localStorage.setItem('token', response.data.token);
        }
        return response.data;
    },

    async logout(): Promise<void> {
        await apiClient.post('/api/auth/logout/');
        localStorage.removeItem('token');
    },

    async getCurrentUser() {
        const response = await apiClient.get('/api/auth/user/');
        return response.data;
    }
};

export default auth;