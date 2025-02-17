from database.model.deliver import Deliver
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database.conn.connection import db


router = APIRouter()


@router.get('/{driver_seq}', status_code=200)
async def driver(session : Session = Depends(db.session), driver_seq : int = None):
    try :
        drivers = session.query(
            Deliver.id,
            Deliver.driver_seq,
            Deliver.hub_id,
            Deliver.truck_id,
            Deliver.order_id,
            Deliver.start_date,
            Deliver.end_date,
            Deliver.delivery_type
            ).filter(
                Deliver.driver_seq == driver_seq
            ).all()
        if not drivers :
            raise HTTPException(status_code=404, detail='drivers not found')
        return {'result' : [
                {
                    'id' : driver[0],
                    'driver_seq' : driver[1],
                    'hub_id' : driver[2],
                    'truck_id' : driver[3],
                    'order_id' : driver[4],
                    'start_date' : driver[5],
                    'end_date' : driver[6],
                    'delivery_type' : driver[7]
                }
                for driver in drivers
            ]
        }
    except Exception as e :
        return {'result' : e}