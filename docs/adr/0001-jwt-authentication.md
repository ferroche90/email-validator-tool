# ADR-0001: JWT for Authentication

## Status

Accepted

## Context

The Email Validator Tool needs a secure authentication mechanism for API access. We considered several authentication approaches:

1. **API Keys Only**: Simple but limited security and no user context
2. **Session-based Authentication**: Requires server-side session storage
3. **OAuth 2.0**: Complex for our use case, overkill for internal tools
4. **JWT (JSON Web Tokens)**: Stateless, secure, and widely supported

The main requirements are:
- Secure API access control
- Stateless authentication (no server-side session storage)
- Support for different permission levels (user vs admin)
- Easy integration with frontend applications
- Industry-standard approach

## Decision

We will implement JWT-based authentication with the following characteristics:

- **Token Generation**: API keys are exchanged for JWT tokens via `/api/token` endpoint
- **Token Structure**: JWTs contain user role, permissions, and expiration time
- **Token Validation**: All protected endpoints validate JWT tokens in Authorization header
- **Token Expiration**: 60-minute access tokens with configurable TTL
- **Algorithm**: HS256 for token signing
- **Secret Management**: Environment-based JWT secret with secure defaults

## Consequences

### Positive

- **Stateless**: No server-side session storage required, scales horizontally
- **Standard**: JWT is widely supported and well-documented
- **Secure**: Tokens are signed and can include expiration and claims
- **Flexible**: Easy to add claims and permissions without database lookups
- **Frontend-friendly**: Works seamlessly with React and other SPA frameworks
- **Stateless**: Reduces database load and simplifies deployment

### Negative

- **Token Size**: JWTs are larger than simple API keys
- **Revocation**: Cannot easily revoke individual tokens (requires blacklisting)
- **Complexity**: More complex than simple API key authentication
- **Security**: If JWT secret is compromised, all tokens become vulnerable
- **Debugging**: Token contents are encoded, harder to debug than plain API keys

### Neutral

- **Performance**: Token validation requires cryptographic operations
- **Storage**: Frontend must securely store tokens (localStorage/sessionStorage)
- **Refresh**: Need to handle token expiration and renewal gracefully

## Implementation Notes

### Backend Implementation
```python
# JWT configuration in backend/app/auth/jwt.py
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "dev-secret-key")
JWT_ALGORITHM = "HS256"
JWT_ACCESS_TOKEN_EXPIRE_MINUTES = 60

# Token generation
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    return encoded_jwt
```

### Frontend Integration
```typescript
// Automatic token management in frontend/src/lib/useAuth.ts
const getToken = async (): Promise<string> => {
  const response = await api.post('/api/token', { api_key: API_KEY })
  return response.data.access_token
}
```

### Security Considerations
- JWT secret must be at least 32 characters in production
- Tokens should be stored in httpOnly cookies for web apps
- Implement token refresh mechanism for long-running sessions
- Consider implementing token blacklisting for logout functionality

## References

- [JWT RFC 7519](https://tools.ietf.org/html/rfc7519)
- [FastAPI JWT Authentication](https://fastapi.tiangolo.com/tutorial/security/)
- [JWT.io](https://jwt.io/) - JWT debugger and documentation

## Related ADRs

- None (this is the first ADR)

---

**ADR Template Version**: 1.0  
**Last Updated**: 2024-12-26  
**Author**: Core Team 