import streamlit as st
import pandas as pd

# ✅ 1. 페이지 설정
st.set_page_config(page_title="🚗 자동차 스펙 비교기", layout="wide")

# ✅ 2. 데이터 불러오기
file_path = 'all-vehicles-model@public.csv'
df = pd.read_csv(file_path, sep=';')

# ✅ 3. 필요한 칼럼만 추출
useful_columns = [
    'make', 'model', 'year', 'engine_displacement',
    'fuel_type', 'transmission',
    'combined_mpg_for_fuel_type1', 'annual_fuel_cost_for_fuel_type1'
]
vehicle_df = df[useful_columns].dropna().reset_index(drop=True)

# ✅ 4. 칼럼 이름 정리
vehicle_df.rename(columns={
    'make': '브랜드',
    'model': '모델명',
    'year': '연식',
    'engine_displacement': '배기량 (L)',
    'fuel_type': '연료',
    'transmission': '변속기',
    'combined_mpg_for_fuel_type1': '복합연비 (mpg)',
    'annual_fuel_cost_for_fuel_type1': '연간 연료비 (USD)'
}, inplace=True)

# ✅ 5. 차량 이미지 매칭 (간단 예시)
car_images = {
    ("Ford", "Bronco 4WD"): "https://upload.wikimedia.org/wikipedia/commons/e/e1/2021_Ford_Bronco.jpg",
    ("Chevrolet", "S10 Pickup"): "https://upload.wikimedia.org/wikipedia/commons/6/6f/1995_Chevrolet_S-10_4x4.jpg",
    ("Honda", "Accord"): "https://upload.wikimedia.org/wikipedia/commons/0/0e/2018_Honda_Accord.jpg",
}
default_image_url = "https://via.placeholder.com/300x200?text=No+Image"

# ✅ 6. Streamlit 제목
st.markdown("<h1 style='text-align: center;'>🚗 차량 스펙 비교기 (브랜드 → 모델 → 연식)</h1>", unsafe_allow_html=True)
st.markdown("---")

# ✅ 7. 3개의 차량 선택
select_cols = st.columns(3)
selected_vehicles = []

for i in range(3):
    with select_cols[i]:
        st.markdown(f"### 🚘 차량 {i + 1} 선택")

        selected_brand = st.selectbox(
            f"브랜드 선택 {i + 1}",
            vehicle_df['브랜드'].unique(),
            key=f"brand_{i}"
        )

        filtered_models = vehicle_df[vehicle_df['브랜드'] == selected_brand]['모델명'].unique()
        selected_model = st.selectbox(
            f"모델명 선택 {i + 1}",
            filtered_models,
            key=f"model_{i}"
        )

        filtered_years = vehicle_df[
            (vehicle_df['브랜드'] == selected_brand) & (vehicle_df['모델명'] == selected_model)
            ]['연식'].sort_values(ascending=False).unique()
        selected_year = st.selectbox(
            f"연식 선택 {i + 1}",
            filtered_years,
            key=f"year_{i}"
        )

        selected_vehicle = vehicle_df[
            (vehicle_df['브랜드'] == selected_brand) &
            (vehicle_df['모델명'] == selected_model) &
            (vehicle_df['연식'] == selected_year)
            ].iloc[0]
        selected_vehicles.append(selected_vehicle)

# ✅ 8. 복합연비 최고 차량 찾기
best_fuel_efficiency_idx = -1
best_fuel_efficiency_value = -1

for idx, vehicle in enumerate(selected_vehicles):
    if vehicle['복합연비 (mpg)'] > best_fuel_efficiency_value:
        best_fuel_efficiency_value = vehicle['복합연비 (mpg)']
        best_fuel_efficiency_idx = idx

# ✅ 9. 비교 결과 출력
st.markdown("---")
st.subheader("📊 선택한 차량 스펙 비교")

spec_cols = st.columns(3)
spec_list = ['브랜드', '모델명', '연식', '배기량 (L)', '연료', '변속기', '복합연비 (mpg)', '연간 연료비 (USD)']

for i, col in enumerate(spec_cols):
    with col:
        vehicle = selected_vehicles[i]

        # 차량 브랜드 + 모델명 키
        key = (vehicle['브랜드'], vehicle['모델명'])
        image_url = car_images.get(key, default_image_url)

        # ✅ 차량 이미지 띄우기
        st.image(image_url, use_column_width=True)

        # ✅ 차량명 + 연식 (⭐️ 강조 포함)
        title = f"{vehicle['브랜드']} {vehicle['모델명']} ({vehicle['연식']})"
        if i == best_fuel_efficiency_idx:
            title += " ⭐️"

        st.markdown(f"<h3 style='text-align: center; margin-top: 20px; margin-bottom: 20px;'>{title}</h3>", unsafe_allow_html=True)

        # ✅ 차량 스펙 출력
        for spec in spec_list:
            st.markdown(f"""
            <div style='
                text-align: center;
                margin-bottom: 12px;
                font-size: 16px;
            '>
                <b>{spec}</b>: {vehicle[spec]}
            </div>
            """, unsafe_allow_html=True)

# ✅ 10. 비교 결과 다운로드 기능 추가

# 3개 차량의 비교 데이터를 하나의 DataFrame으로 만들기
compare_result = pd.DataFrame(selected_vehicles)

# 필요한 컬럼만 추려서 다운로드
compare_result = compare_result[spec_list]

# 다운로드 버튼
st.markdown("---")
st.subheader("📥 비교 결과 다운로드")

csv = compare_result.to_csv(index=False).encode('utf-8-sig')

st.download_button(
    label="CSV 파일 다운로드",
    data=csv,
    file_name='차량_비교_결과.csv',
    mime='text/csv'
)