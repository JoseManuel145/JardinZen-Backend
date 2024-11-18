from pydantic import BaseModel


class Info(BaseModel):
    name: str
    description: str


class NurseryBase(BaseModel):
    info: Info
    ubication: str
    

    class Config:
        from_attributes = True


class NurseryRequest(NurseryBase):
    id_manager: int


class NurseryResponse(NurseryBase):
    id_nursery: int

    class Config:
        from_attributes = True
