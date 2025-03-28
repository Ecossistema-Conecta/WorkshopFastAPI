from fastapi import Depends, HTTPException, APIRouter
from fastapi.security import HTTPBasic, HTTPBasicCredentials

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database import get_session
from app.models import User
from app.schemas import UserSchema, UserSchemaResponse, UserLeaderSchema
from app.security.hash_password import HashPassword


router = APIRouter(tags=["Users"])
security = HTTPBasic()

@router.post("/register", response_model=UserSchemaResponse, status_code=201)
async def create_user(data: UserSchema, db=Depends(get_session)):
    """Cria um novo usuário.
    
    ### Parâmetros:
    - **username**: Nome de usuário a ser criado.
    - **password**: Senha do usuário.
    
    ### Retorno:
    - **[UserSchemaResponse](../../../schemas/#app.schemas.UserSchemaResponse)**: Dados do usuário criado.

    ### Exceções:
    - **400**: Se um usuário com o mesmo nome já existir.
    
    ### Exemplo de JSON de Entrada:
    ```json
        {
            "username": "johndoe",
            "password": "securepassword"
        }
    ```    
    """
        
    existing_user = db.query(User).filter(User.username == data.username).first()

    if existing_user:
        raise HTTPException(status_code=400, detail="Usuário já existe")
    
    hashed_password = HashPassword.hash(data.password)

    user_instance = User(username=data.username, password=hashed_password)

    db.add(user_instance)

    try:
        db.commit()
        db.refresh(user_instance)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=500, detail="Erro ao criar usuário.")
    
    return UserSchemaResponse(id=user_instance.id, username=user_instance.username, is_leader=user_instance.is_leader)


@router.post("/registerLeader", response_model=UserSchemaResponse, status_code=201)
async def create_user(data: UserLeaderSchema, db=Depends(get_session)):
    """Este é um endpoint secreto que cria um novo usuário líder.
        ### Parâmetros:
        - **username**: Nome de usuário a ser criado.
        - **password**: Senha do usuário.
        - **is_leader**: Indica se o usuário é líder (padrão: True).
        ### Retorno:
        - **[UserSchemaResponse](../../../schemas/#app.schemas.UserSchemaResponse)**: Dados do usuário criado.
        ### Exceções:
        - **400**: Se um usuário com o mesmo nome já existir.
        ### Exemplo de JSON de Entrada:
        ```json
            {
                "username": "johndoe",
                "password": "securepassword",
                "is_leader": true
            }
        ```
    """
        
    existing_user = db.query(User).filter(User.username == data.username).first()

    if existing_user:
        raise HTTPException(status_code=400, detail="Usuário já existe")
    
    hashed_password = HashPassword.hash(data.password)

    user_instance = User(username=data.username, password=hashed_password, is_leader=data.is_leader)

    db.add(user_instance)

    try:
        db.commit()
        db.refresh(user_instance)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=500, detail="Erro ao criar usuário.")
    
    return UserSchemaResponse(id=user_instance.id, username=user_instance.username, is_leader=user_instance.is_leader)


@router.post("/login")
async def login(credentials: HTTPBasicCredentials = Depends(security), db: Session = Depends(get_session)):
    """Autenticação básica com verificação de senha.
    
    ### Parâmetros:
    - header: **Authorization**: Credenciais de autenticação no formato.
    - `Basic base64(username:password)`.
    
    ### Retorno:
    - **message**: Mensagem de boas-vindas ao usuário.
    
    ### Exceções:
    - **401**: Se as credenciais ou formatação estiverem incorretas.
    """
    
    user = db.query(User).filter(User.username == credentials.username).first()
    
    if not user or not HashPassword.compair(credentials.password, user.password):
        raise HTTPException(status_code=401, detail="Credenciais inválidas")
    
    return {"message": f"Boas vindas, {user.username}, seu login bem-sucedido!"}