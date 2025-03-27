from fastapi import Depends, HTTPException, APIRouter

from sqlalchemy.exc import IntegrityError

from app.database import get_session
from app.models import User
from app.schemas import UserSchema, UserSchemaResponse

router = APIRouter(prefix="/users", tags=["Users"])

@router.post("/", response_model=UserSchemaResponse, status_code=201)
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
    existing_user = db.query(User).filter(data.username == data.username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Usuário já existe")
    
    user_data = data.model_dump()
    user_instance = User(**user_data)

    db.add(user_instance)
    try:
        db.commit()
    except IntegrityError as ie:
        db.rollback()
        return {"error": str(ie.orig)}

    db.refresh(user_instance)

    return UserSchemaResponse(id=user_instance.id, username=user_instance.username, is_leader=user_instance.is_leader)
