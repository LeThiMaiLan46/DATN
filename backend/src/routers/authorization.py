import os
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi import status
import requests
bearer_scheme = HTTPBearer()

def verify(api_key):
    return 1
    # try:
    #     res = requests.post("https://api-nxdev.ntq.ai/api/keys/verify",json={"encoded":api_key}).json()
    #     if "userId" not in res:
    #         return -1
    #     return res
    # except Exception as err:
    #     return -1
async def authenticate(bearer: HTTPAuthorizationCredentials = Depends(bearer_scheme)):
    if (bearer.credentials != "03282b35614ad1656d304") and (verify(bearer.credentials)==-1):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Invalid or expired token',
            headers={'WWW-Authenticate': 'Bearer'},
        )
    return {"status": "ok"}
