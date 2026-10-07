import { describe, it, expect } from 'vitest';

describe('Frontend Smoke Test', () => {
  it('basic arithmetic works', () => {
    expect(1 + 1).toBe(2);
  });

  it('verifies environment default API origin', () => {
    const origin = process.env.API_ORIGIN || 'http://localhost:8000';
    expect(origin).toBe('http://localhost:8000');
  });
});
