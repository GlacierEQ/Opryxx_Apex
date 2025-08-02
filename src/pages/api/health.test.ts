import { createMocks } from 'node-mocks-http';
import handler from './health';

describe('/api/health', () => {
  test('returns a 200 status code', async () => {
    const { req, res } = createMocks({
      method: 'GET',
    });

    await handler(req, res);

    expect(res._getStatusCode()).toBe(200);
    expect(JSON.parse(res._getData())).toEqual({ status: 'ok' });
  });
});
