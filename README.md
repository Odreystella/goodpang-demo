### goodpang-demo
Django를 이용해서 e-commerce를 구현하는 프로젝트입니다.


### 목표
- 인덱싱, 대용량트래픽, 동시성등을 배우기 위해 인프런 강의를 보며 만든 백엔드 프로젝트입니다.


### 알게 된 내용
- **pre-commit**
    - [참고](https://www.daleseo.com/pre-commit/)

- **django orm filter()과 index 사용 여부**
    - index는 검색 속도를 향상시키기 위해 사용되는 자료구조로 빠른 데이터 검색 및 정렬에 활용.
    - ORM에서 filter()할 때 index를 활용하지만 검색 키워드와 같은 같은 결과만 가져옴
    - `__contains`를 사용하면 SQL의 LIKE문을 사용하는데 이때 index 활용 X
    - 즉, 전체 레코드를 풀스캔 하게 되고 검색 성능이 떨어짐
    - (예외) `__startwith`의 경우 LIKE문(left-anchored search)을 사용하는데, 검색 키워드가 중간에 포함된 경우는 해결할 수 없음 

- **postgresql의 Full-text search vs. Elastic Search**
    - `Gin Index`
        - [참고](https://medium.com/vuno-sw-dev/postgresql-gin-%EC%9D%B8%EB%8D%B1%EC%8A%A4%EB%A5%BC-%ED%86%B5%ED%95%9C-like-%EA%B2%80%EC%83%89-%EC%84%B1%EB%8A%A5-%EA%B0%9C%EC%84%A0-3c6b05c7e75f)
    - postgresql의 Full-text search 영문 데이터 구현 방법
        - SearchVectorField: 영문 데이터인 tags를 기준으로 형태소 분석한 결과를 저장하는 필드.
        - GinIndex: search_vector 필드를 기준으로 역인덱스 생성.
        - SearchVector: 텍스트를 토큰화하고 정규화하여 검색 가능한 형태로 변환.
            - PostgreSQL의 to_tsvector 함수를 기반으로 동작
            - 각 단어와 해당 단어의 위치를 나타내는 토큰들로 구성
        - SearchQuery: 검색어를 데이터베이스가 SearchVector와 비교하는 검색 쿼리 객체로 변환.
            - search_type 옵션을 줄 수 있음
            - 검색어는 stemming algorithms(형태소 분석 알고리즘)을 거침
        - tsvector_update_trigger: tags가 수정될 때, search_vector과 역인덱스를 수정하는 트리거. [참고](https://medium.com/@nandagopal05/django-full-text-search-with-postgresql-f063aaf34e35)
    - postgresql의 Full-text search 한글 데이터 구현 방법
        - PostgreSQL 익스텐션 `pg_bigm` 사용
            - Dockerfil에서 postgres15 이미지를 사용할 때 pg_bigm(2-gram) 같이 설치해줌
            - bi-gram은 두 개의 연속된 문자마다 인덱스를 생성하는 방식
                - 예. "postgresql" -> ["po", "os", "st", "tg", "gr", "re", "es"]

- **postgres 실행계획 보기**
    - `EXPLAIN SELECT * from product where name like '%멋있는%';`
    - `Seq Scan on product`: product를 full scan 한다는 의미.
    - `Bitmap Index Scan on product_name_gin_index`: 생성한 인덱스를 사용해서 scan 한다는 의미.
        - 데이터 셋: 10만개, 12,800개 이상 데이터가 조회될 때부터 사용되었음.

- **대용량 트래픽 처리 노하우**
    - 결국 얼마만큼 미리 계산해둘 것인지가 중요
    - 어플리케이션 관점
        - 비동기 처리
        - 데이터베이스 쿼리/인덱스 튜닝
            - Index 생성 & 검색 엔진
        - 캐싱
            - Redis, Memcached, CDN
        - 통계 데이터
            - 실시간 계산보다 미리 계산해서 통계 테이블 만들면 빠른 조회 가능
    - 인프라 관점
        - Scale Up/Scale Out
        - 로드 밸런싱
        - Event-driven Architecture
        - 데이터베이스 샤딩/파티셔닝
        - CDN
