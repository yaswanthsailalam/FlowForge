import { workspaceService } from '../services/workspace.service';
import api from '../lib/api-client';

jest.mock('../lib/api-client');

describe('workspaceService', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  test('listWorkspaces calls correct endpoint', async () => {
    const mockWorkspaces = [{ workspace_id: 'ws1', name: 'WS 1' }];
    api.get.mockResolvedValueOnce({ data: mockWorkspaces });

    const result = await workspaceService.listWorkspaces();

    expect(api.get).toHaveBeenCalledWith('/workspaces/');
    expect(result).toEqual(mockWorkspaces);
  });

  test('createWorkspace calls correct endpoint with data', async () => {
    const mockWorkspace = { workspace_id: 'ws2', name: 'WS 2' };
    api.post.mockResolvedValueOnce({ data: mockWorkspace });

    const result = await workspaceService.createWorkspace({ name: 'WS 2' });

    expect(api.post).toHaveBeenCalledWith('/workspaces/', { name: 'WS 2' });
    expect(result).toEqual(mockWorkspace);
  });
});
