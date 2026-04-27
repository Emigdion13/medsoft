import { request } from '@playwright/test';

export const createAPIContext = async (baseURL: string) => {
  return await request.newContext({
    baseURL,
    headers: {
      'Content-Type': 'application/json',
    },
  });
};

export interface AuthTokens {
  access: string;
  refresh: string;
}

export const performLogin = async (
  apiContext: any,
  username = 'admin',
  password = 'admin'
): Promise<AuthTokens> => {
  const response = await apiContext.post('/api/auth/login/', {
    data: { username, password },
  });

  if (!response.ok()) {
    throw new Error(`Login failed: ${await response.text()}`);
  }

  return await response.json();
};

export const getAuthenticatedContext = async (
  baseURL: string,
  username = 'admin',
  password = 'admin'
) => {
  const apiContext = await createAPIContext(baseURL);
  const { access } = await performLogin(apiContext, username, password);

  return {
    context: apiContext,
    token: access,
  };
};
