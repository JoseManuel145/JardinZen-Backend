from pydantic import BaseModel


class Info(BaseModel):
    name: str
    description: str


class NurseryBase(BaseModel):
    info: Info
    ubication: str
    

    class Config:
        orm_mode = True


class NurseryRequest(NurseryBase):
    id_manager: int


class NurseryResponse(NurseryBase):
    id_nursery: int

    class Config:
        orm_mode = True
