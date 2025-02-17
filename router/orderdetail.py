from database.model.orderdetail import OrderDetail
from database.model.product import Product
from database.model.order import Order
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc, func, cast, String, Integer, asc
from database.conn.connection import db
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import calendar





router = APIRouter()

## -----------------관리자용---------------

# 관리자용 매출 연별 조회
@router.get('/year', status_code=200)
async def year(session : Session = Depends(db.session)):
    """
    관리자용
    상품이름, 상품별 판매수량, 상품별 총 합 조회  \n

    <key> \n
    전체 key : result \n
    1. 올해 상품별 매출 표 key : products - (name, order_count, total_price) \n
    2. 최근 6년 상품별 매출 그래프 key : year_sales - (year, sales) \n
    """
    try :
        # 현재 시간 기준 년도
        current_year = datetime.now().strftime('%Y')
        orders = session.query(
            Product.name, # 상품 이름
            func.sum(OrderDetail.quantity).label('order_count'), # 판매 수량
            func.sum(OrderDetail.price).label('total_price'), # 총 합
        ).join(
            Product, 
            Product.id == OrderDetail.product_id
        ).filter(
            cast(func.substring(OrderDetail.id, 1, 2), String) == current_year[2:] # 현재년도 데이터 출력
        ).group_by(
        Product.name
        ).order_by(desc('order_count'))

        if not orders :
            raise HTTPException(status_code=404, detail="detail year not found")
        
        # 년도별 매출 그래프
        years_data = session.query(
            func.substring(func.min(Order.id),1,2).label('year'),
            func.sum(Order.price).label('year_sales'),
        ).group_by(
            func.substring(Order.id,1,2)
        ).all()
        
        if not years_data :
            raise HTTPException(status_code=404, detail='year data not found')

        # 최근 6년 연도 리스트 생성
        recent_years = [str(int(current_year) - i) for i in range(6)]
        
        # 쿼리 결과값을 딕셔너리로 변경
        sales_dict = {year[0]: year[1] for year in years_data}

        # 최근 6년 데이터 생성 (없는 연도는 0으로 설정)
        year_sales_list = [
            {
                'year': year,
                'sales': sales_dict.get(year[2:], 0)
            }
            for year in reversed(recent_years)
        ]
        return {'result': {
            'products': [
                {
                    'name': order[0],
                    'order_count': order[1],
                    'total_price': order[2],
                }
                for order in orders[:5]
            ],
            'year_sales': year_sales_list
        }}
    except Exception as e:
        return {'result' : e}
    


# 관리자용 매출 관리 주별 조회
@router.get('/week', status_code=200)
async def week(session: Session = Depends(db.session)):
    """
    관리자용 매출관리 "월" \n
    상품이름, 상품별 판매수량, 상품별 총 합, 요일별 매출(3개월) \n

    <key>
    전체 key : 'result' \n
    상품 매출 표 key : 'products' 
    -  (name, order_count, total_price) \n
    그래프 key : 'weekday_sales' 
    - (weekday, sales) \n
    """
    try:
        current_date = datetime.now()
        start_of_week = current_date - timedelta(days=current_date.weekday())
        end_of_week = start_of_week + timedelta(days=6)
        
        # 이번주 상품별 매출 표 쿼리
        orders = session.query(
            Product.name,
            func.sum(OrderDetail.quantity).label('order_count'),
            func.sum(OrderDetail.price).label('total_price'),
        ).join(
            Product, 
            Product.id == OrderDetail.product_id
        ).filter(
            cast(func.substring(OrderDetail.id, 1, 6), String).between(
                start_of_week.strftime('%y%m%d'),
                end_of_week.strftime('%y%m%d')
            )
        ).group_by(
            Product.name
        ).order_by(desc('order_count'))

        if not orders:
            raise HTTPException(status_code=404, detail="detail week not found")
        
        # 한 분기의 요일별 매출 그래프 쿼리
        weekday_sales = session.query(
            ((cast(func.extract('dow', Order.order_date), Integer) + 6) % 7).label('weekday'),
            func.sum(Order.price).label('daily_sales'),
        ).filter(
            cast(func.substring(Order.id, 1, 4), String).between(
                (current_date - relativedelta(months=3)).strftime('%y%m'),
                current_date.strftime('%y%m')
            )
        ).group_by(
            func.extract('dow', Order.order_date)
        ).order_by(
            asc('weekday')
        ).all()

        if not weekday_sales :
            raise HTTPException(status_code=404, detail='weekday_sales not found')

        # 요일별 매출 데이터를 딕셔너리로 변환
        sales_dict = {day[0]: day[1] for day in weekday_sales}
        
        # 모든 요일(0-6)에 대해 데이터 생성
        weekday_names = ['월', '화', '수', '목', '금', '토', '일']
        weekday_sales_list = [
            {
                'weekday': weekday_names[day],
                'sales': sales_dict.get(day, 0)
            }
            for day in range(7)  # 0(월요일)부터 6(일요일)까지
        ]

        return {'result': {
            "products": [
                {
                    'name': order[0],
                    'order_count': order[1],
                    'total_price': order[2]
                }
                for order in orders[:5]
            ],
            'weekday_sales': weekday_sales_list
        }}
    except Exception as e:
        return {'result': e}    
    
    
# 관리자용 매출 관리 월별 조회 (상품별 매출 표)
@router.get('/month', status_code=200)
async def month(session : Session = Depends(db.session)):
    """
    관리자용 매출관리 "월" \n
    매출관리 페이지 월별 매출 표 \n


    key : result \n
    -  (name, order_count, total_price)
    
    """
    try :
        # 현재 시간 기준 월
        current = datetime.now()
        orders = session.query(
            Product.name, # 상품 이름
            func.sum(OrderDetail.quantity).label('order_count'), # 판매 수량
            func.sum(OrderDetail.price).label('total_price'), # 총 합
        ).join(
            Product, 
            Product.id == OrderDetail.product_id
        ).filter(
            func.substring(OrderDetail.id, 1, 2) == current.strftime("%y"),
            func.substring(OrderDetail.id,3,2) == current.strftime("%m")
        ).group_by(
        Product.name
        ).order_by(desc('order_count'))
        if not orders :
            raise HTTPException(status_code=404, detail="detail month not found")
        
        #  # 월별 매출 쿼리
        months_data = session.query(
            func.substring(func.min(Order.id),3,2).label('month'),
            func.sum(Order.price).label('month_price'),
        ).filter(
            cast(func.substring(Order.id, 1, 4), String).between(
                (current - relativedelta(months=5)).strftime('%y%m'),
                current.strftime('%y%m')
            )
        ).group_by(
            func.substring(Order.id,3,2)
        ).order_by(
            func.substring(Order.id,3,2).desc()
        ).all()

        if not months_data:
            raise HTTPException(status_code=404, detail='months not found')
            
        # 월별 매출 데이터 변환
        sales_dict = {month[0]: month[1] for month in months_data}

        # 최근 6개월의 월 리스트 생성
        months_list = []
        for i in range(6):
            past_date = current - relativedelta(months=i)
            months_list.append(past_date.strftime('%Y%m'))
            
        
        # # # 최근 6개월 데이터 생성 (없는 월은 0으로 설정)
        month_sales_list = [
            {
                'month': f"{month[:4]}.{month[-2:]}",
                'sales': sales_dict.get(month[-2:], 0)
            }
            for month in reversed(months_list)
        ]

        return {'result' : 
                    { "products":[
                        {
                            'name' : order[0],
                            'order_count' : order[1],
                            'total_price' : order[2]
                        }
                        for order in orders
                    ],
                    "month_sales" : month_sales_list
                    }

                }
    except Exception as e:
        return {'result' : e}

@router.get('/home', status_code=200)
async def dashboard(session : Session = Depends(db.session)): 
    """
    관리자 dashboard \n
    1. 최근 주문  "key" = result \n
    - count : 대표 상품 외 상품 갯수 \n
    - price : 주문별 금액 \n
    - quantity : \n

    2. 카테고리별 판매율 key = category_sales \n
    - category_id : 카테고리 id, \n
    - category_name: 카테고리명, \n
    - total_sales : 카테고리별 매출 \n

    """
    try :   
        dashs = session.query(
            OrderDetail.id,
            OrderDetail.name, # 유저 이름
            func.min(Product.name).label('name'), # 최근주문 상품 이름
            func.count(Product.name).label('count'), # 최근주문 유저별 대표 상품 외 갯수(ex: 볼펜 외 "2"개)
            func.sum(OrderDetail.price).label('price'), # 최근 주문 유저별 주문 금액(합)
            func.sum(func.sum(OrderDetail.price)).over().label('total_price'), # 총 매출
            func.sum(func.count("*")).over().label('total_order'), # 총 주문 
            func.min(Order.status) # 주문별 배송 상태
        ).join(
            Product,
            Product.id == OrderDetail.product_id
        ).join(
            Order,
            Order.id == OrderDetail.id
        ).group_by(
            OrderDetail.id,
            OrderDetail.name
        ).order_by(
            func.substring(OrderDetail.id, 0, 12).desc()
        ).all()
        if not dashs : 
            raise HTTPException(status_code=404, detail='dashs not found')

        
        return {
            'result' :[
            {
                'id' : dash[0],
                'user_name' : dash[1],
                'product_name' : dash[2],
                'count' : dash[3]-1,
                'price' : dash[4],
                'status' : dash[7],
            }
            for dash in dashs[:5]
        ],
        'total_price' : dashs[0][5],
        'total_order' : dashs[0][6],
        }
    except Exception as e :
        print(e)
        return {'result' : e}


## --------------------유저 --------------------------

# 주문시 orderdetail 입력
@router.post('/', status_code=200)
async def insert(session : Session = Depends(db.session), id : str = None,user_seq : int = None, product_id : int = None, price : float = None, quantity : int = None, name : str = None):
    """
    사용자용 \n
    주문시 orderdetail 입력 \n
    - id : 주문번호 \n
    - user_seq : 유저 seq \n
    - product_id : 상품 코드 \n
    - price : 상품 가격 \n
    - quantity : 주문수량 \n
    - name : 유저 이름 
    """
    try :
        new_order = OrderDetail(
            id = id,
            user_seq = user_seq,
            product_id = product_id,
            price = price,
            quantity = quantity,
            name = name
        )
        session.add(new_order)
        session.commit()
        return {'result' : 'ok'}
    except Exception as e:
        return {'result' : e}


@router.get('/{user_seq}', status_code=200)
async def select_orderlist(session : Session = Depends(db.session), user_seq : int = None):
    """
    주문내역 불러오기 \n
    대표상품 : name, quantity,image \n
    총 합 : price \n
    count : 주문 상품 갯수 -1  \n
    """
    try:
        lists = session.query(
            OrderDetail.id,
            func.min(Product.image).label('image'),
            func.min(Product.name).label('name'),
            func.count(OrderDetail.name).label('count'),
            func.min(OrderDetail.quantity).label('quantity'),
            # func.sum(OrderDetail.price).label('price'),
            func.min(Order.price)
            ).join(
                Product,
                Product.id == OrderDetail.product_id,
            ).join(
                Order,
                Order.id == OrderDetail.id
            ).filter(
                OrderDetail.user_seq  == user_seq,
            ).group_by(
                OrderDetail.id,
                OrderDetail.user_seq
            ).order_by(
                func.substring(OrderDetail.id,0,12).desc()
            )
        if not lists :
            raise HTTPException(status_code=404, detail="orderlist not found")
        return {'result' : [
            {
                "id" : list[0],
                "image" : list[1],
                "name" : list[2],
                "count" : list[3]-1,
                "quantity" : list[4],
                "price" : list[5],
                "date" : f"20{list[0][:2]}.{list[0][2:4]}.{list[0][4:6]}"
            }
            for list in lists
                ]
        }
    except Exception as e:
        return {'result' : e}


