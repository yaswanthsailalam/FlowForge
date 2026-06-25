import { authService } from '../services/auth.service';
import api from '../lib/api-client';

jest.mock('../lib/api-client');

describe('authService', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  test('login calls api with correct data', async () => {
    const mockToken = { access_token: 'test-token', token_type: 'bearer' };
    api.post.mockResolvedValueOnce({ data: mockToken });

    const result = await authService.login('test@example.com', 'password123');

    expect(api.post).toHaveBeenCalledWith('/auth/login', expect.any(FormData), {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
    });
    expect(result).toEqual(mockToken);
  });

  test('getCurrentUser calls correct endpoint', async () => {
    const mockUser = { user_id: '123', email: 'test@example.com' };
    api.get.mockResolvedValueOnce({ data: mockUser });

    const result = await authService.getCurrentUser();

    expect(api.get).toHaveBeenCalledWith('/users/me');
    expect(result).toEqual(mockUser);
  });
});
