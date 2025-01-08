import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm

client_id = '8a791f98f5044fa896dc2430d570500c'
client_secret = '7976fc4cecd94f9e9761bf4fe30c4df1'

sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id=client_id,
                                                           client_secret=client_secret))

# 한글 폰트 설정 함수
def set_font():
    font_path = 'C:/Windows/Fonts/NanumGothic.ttf'  # Windows용 폰트 경로
    font_prop = fm.FontProperties(fname=font_path)
    plt.rc('font', family=font_prop.get_name())

# ===== 2. 곡 데이터 검색 및 수집 =====
def search_tracks(query, limit=20):
    results = sp.search(q=query, limit=limit)
    track_data = []
    
    for track in results['tracks']['items']:
        track_info = {
            '곡명': track['name'],
            '아티스트': track['artists'][0]['name'],
            '앨범': track['album']['name'],
            '발매 연도': track['album']['release_date'][:4],
            '인기 점수': track['popularity'],
            '트랙 ID': track['id']
        }
        track_data.append(track_info)
    
    return pd.DataFrame(track_data)

# ===== 3. SQLite 데이터베이스 연결 및 테이블 생성 =====
def create_database():
    conn = sqlite3.connect('spotify_data.db')
    cursor = conn.cursor()
    
    # 기존 테이블 삭제 후 새로운 테이블 생성
    cursor.execute('''DROP TABLE IF EXISTS tracks;''')
    cursor.execute(''' 
    CREATE TABLE IF NOT EXISTS tracks (
        track_id TEXT PRIMARY KEY,
        title TEXT,
        artist TEXT,
        album TEXT,
        release_year INTEGER,
        popularity INTEGER
    )
    ''')
    conn.commit()
    conn.close()

# ===== 4. 데이터 삽입 =====
def insert_data(df):
    conn = sqlite3.connect('spotify_data.db')
    cursor = conn.cursor()
    
    for _, row in df.iterrows():
        cursor.execute('''
        INSERT OR IGNORE INTO tracks (track_id, title, artist, album, release_year, popularity)
        VALUES (?, ?, ?, ?, ?, ?)
        ''', (row['트랙 ID'], row['곡명'], row['아티스트'], row['앨범'], row['발매 연도'], row['인기 점수']))
    
    conn.commit()
    conn.close()

# ===== 5. 데이터 조회 =====
def get_tracks_from_db():
    conn = sqlite3.connect('spotify_data.db')
    df = pd.read_sql_query("SELECT * FROM tracks", conn)
    conn.close()
    return df

# ===== 6. 데이터 시각화 =====
def plot_popularity(artist_name):
    set_font()  # 한글 폰트 설정
    df = get_tracks_from_db()
    
    # 아티스트 이름에 기반하여 제목 생성
    plt.figure(figsize=(12, 6))
    
    # 점수 구간별 색상 설정
    colors = []
    for popularity in df['popularity']:
        if popularity <= 20:
            colors.append('yellow')  # 0~20점: 노란색
        elif popularity <= 40:
            colors.append('green')  # 21~40점: 초록색
        elif popularity <= 60:
            colors.append('blue')  # 41~60점: 파란색
        else:
            colors.append('red')  # 61점 이상: 빨간색
    
    # 막대 그래프 그리기
    plt.bar(df['title'], df['popularity'], color=colors)
    plt.xticks(rotation=45, ha='right')  # x축 레이블을 오른쪽으로 회전하여 겹치지 않게 함
    
    # 제목 동적 변경
    plt.title(f'{artist_name} 인기 곡 분석 및 점수')
    plt.ylabel('인기 점수')
    plt.xlabel('곡명')
    
    # 레이아웃 자동 조정 (제목과 레이블이 잘리지 않도록)
    plt.tight_layout()  
    plt.show()

# ===== 7. 메인 실행 =====
if __name__ == '__main__':
    artist = '히게단'  # 원하는 아티스트 이름 입력

    create_database()
    
    # 해당 아티스트의 인기곡 20곡 검색 및 저장
    df = search_tracks(artist, limit=20)
    print(df)
    insert_data(df)
    
    # 저장된 데이터 확인
    saved_data = get_tracks_from_db()
    print("DB에 저장된 데이터: ")
    print(saved_data)
    
    # 시각화 실행 (동적으로 제목 변경)
    plot_popularity(artist)
