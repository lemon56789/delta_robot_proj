# IK Structure Note

이 문서는 델타 로봇 inverse kinematics를 `2atan(t)` 기반 대수적 풀이 관점에서 참고용으로 정리한 메모다.
현재 문서는 구현 채택안이나 Source of Truth가 아니라, reference 기반 식 구조 이해와 프로젝트 변수 매핑을 돕기 위한 정리다.

## 1. Purpose
- 델타 로봇 IK의 핵심 수식 흐름을 짧게 정리한다.
- 논문식 일반 변수와 현재 프로젝트 기구 변수 사이의 대응 관계를 맞춘다.
- 후속 `E`, `F`, `G` 유도와 코드 구현 전에 공통 언어를 만든다.

## 2. Core Flow
`2atan(t)` 기반 IK의 핵심 흐름은 아래와 같다.

1. 각 arm에 대해 링크 길이 제약식을 둔다.
2. 위치 벡터를 프로젝트 좌표계로 전개한다.
3. 식을 `E_i cos(theta_i) + F_i sin(theta_i) + G_i = 0` 형태로 정리한다.
4. `t_i = tan(theta_i / 2)` 치환을 적용한다.
5. `t_i`에 대한 2차식 해를 구한다.
6. `theta_i = 2 atan(t_i)`로 각도를 복원한다.

핵심 요약:
- 길이 제약
- 삼각함수 방정식
- 반각 치환
- 각도 복원

## 3. IK Implementation Flow
구현 순서는 아래처럼 잡으면 된다.

1. 입력 `(x, y, z)`를 `base_frame` 기준 `mm`로 받는다.
2. arm 방향벡터 `e_1`, `e_2`, `e_3`를 기준으로 각 arm의 `B_i`, `P_i`, `J_i(theta_i)` 구조를 잡는다.
3. 각 arm에 대해 `E_i`, `F_i`, `G_i`를 계산한다.
4. 판별식 `D_i = E_i^2 + F_i^2 - G_i^2`를 계산하고, `D_i < 0`이면 `reject`한다.
5. `t_i = (-F_i ± sqrt(D_i)) / (G_i - E_i)`로 두 해를 계산한다.
6. `theta_i = 2 atan(t_i)`로 각도를 복원한다.
7. 임시 working range `0 deg <= theta_i <= 90 deg`와 `downward-working branch` 조건으로 유효한 해만 남긴다.
8. 유효 후보가 둘이면 `previous_theta_i`와 가장 가까운 해를 선택한다.
9. 세 arm 모두 유효하면 `(theta1, theta2, theta3)`를 반환하고, 하나라도 실패하면 `reject`한다.

## 4. Length Constraint
각 arm `i`에 대해 parallelogram link length는 상수다.

`|l_i|^2 = l^2`

또는 성분 기준으로 쓰면:

`l^2 = l_{ix}^2 + l_{iy}^2 + l_{iz}^2`

여기서:
- `i`는 `1, 2, 3` arm index
- `l_i`는 upper arm 끝점에서 platform 연결점까지의 link vector
- `l`은 [system_data_flow.md](/home/lemon56789/delta_robot/docs/system_data_flow.md)에서 정의한 parallelogram link length

## 5. Generic Algebraic Form
좌표를 대입하면 arm `i`별로 최종적으로 아래 구조를 목표로 한다.

`E_i cos(theta_i) + F_i sin(theta_i) + G_i = 0`

이후 반각 치환:

`t_i = tan(theta_i / 2)`

를 쓰면 `theta_i` 대신 `t_i`에 대한 대수식으로 정리할 수 있다.

논문식 해 구조는 다음과 같이 쓸 수 있다.

`t_i = (-F_i ± sqrt(E_i^2 + F_i^2 - G_i^2)) / (G_i - E_i)`

`theta_i = 2 atan(t_i)`

현재 단계에서 중요한 점:
- `E_i`, `F_i`, `G_i`는 우리 좌표계와 기구 정의 기준으로 정리되어 있어야 한다.
- `±` 두 해 중 물리적으로 가능한 해를 선택하는 규칙이 필요하다.

## 6. Project Variable Mapping
현재 프로젝트에서 이미 정의된 기호는 [system_data_flow.md](/home/lemon56789/delta_robot/docs/system_data_flow.md)를 따른다.

좌표 및 기구 변수:
- `O`: `base_frame` 원점, base center
- `B1`, `B2`, `B3`: base side center에 위치한 각 arm의 motor position
- `P1`, `P2`, `P3`: platform의 각 연결점
- `L`: motor-driven upper arm length
- `l`: parallelogram link length
- `sB`: base triangle side length
- `uB`: base center to vertex distance
- `wB`: base center to side distance
- `sP`: platform triangle side length
- `uP`: platform center to vertex distance
- `wP`: platform center to side distance
- end-effector center position: `(x, y, z)` 또는 interface 상 `target_x`, `target_y`, `target_z`
- motor angles: `theta1`, `theta2`, `theta3`

arm index 대응:
- arm 1: `B1`, `P1`, `theta1`
- arm 2: `B2`, `P2`, `theta2`
- arm 3: `B3`, `P3`, `theta3`

좌표식 표기 원칙:
- `B_i` 좌표는 `wB` 기준으로 표현한다.
- `P_i` 좌표는 `uP` 기준으로 표현한다.
- 좌표식 전개에서는 `sB`, `sP`를 직접 쓰지 않고 필요하면 후처리에서 변환한다.

`theta_i` 정의:
- `theta_i`는 arm `i`의 local actuation plane에서 정의되는 upper arm 회전각이다.
- `theta_i = 0 deg`는 upper arm이 `base plane`에 놓인 자세다.
- `theta_i = +90 deg`는 upper arm이 workspace direction인 `-z` 방향과 평행한 자세다.
- `theta_i`의 양의 방향은 upper arm이 `base plane`에서 workspace 방향으로 내려가는 회전 방향이다.

## 7. Vector Interpretation
각 arm `i`에서 필요한 벡터 관계는 개념적으로 다음처럼 볼 수 있다.

- base reference point: `B_i`
- platform connection point: `P_i`
- platform center position: `(x, y, z)`
- upper arm rotation angle: `theta_i`
- upper arm end position: `J_i(theta_i)` 같은 중간 joint position
- parallelogram link vector: `l_i = P_i - J_i`

여기서 `J_i`는 현재 프로젝트 contract field가 아니라, IK 유도에서만 쓰는 보조기호다.
의미는 arm `i`의 upper arm 끝점이자 parallelogram link와 연결되는 elbow joint다.

그러면 IK의 출발점은 다음 길이 제약으로 정리된다.

`|P_i - J_i(theta_i)|^2 = l^2`

이 식을 전개하면 `cos(theta_i)`와 `sin(theta_i)`가 들어가는 항이 생기고, 이를 `E_i`, `F_i`, `G_i`로 묶는 구조가 된다.

## 8. Arm 1 Joint Coordinate Note
arm 1에 대해 아래 가정을 둔 메모 수준 좌표식을 먼저 사용할 수 있다.

- `B1 = (0, -wB, 0)`
- arm 1의 local actuation plane은 `y-z` 평면이다
- `B1`에서 원점 `O` 반대방향의 수평 outward 방향은 `-y`다
- `theta_1 = 0 deg`에서 upper arm은 `base plane` 안에서 `-y` 방향으로 놓인다
- `theta_1`가 증가할수록 upper arm은 `-z` 방향으로 내려간다

그러면 arm 1의 upper arm 끝점은 다음처럼 둘 수 있다.

`J_1(theta_1) = (0, -wB - L cos(theta_1), -L sin(theta_1))`

이 식의 해석:
- `x` 성분은 arm 1 local plane 가정 때문에 `0`
- `y` 성분은 base plane 안의 outward 수평 성분
- `z` 성분은 workspace direction이 `-z`이므로 음수 방향으로 내려간다

이 좌표식은 후속 `|P_1 - J_1|^2 = l^2` 전개의 출발점으로 쓸 수 있다.
다만 아직 `P_1`의 최종 프로젝트 좌표식과 arm 2, arm 3의 일반화는 별도 정리가 필요하다.

같은 기준으로 base side center는 다음처럼 적을 수 있다.

`B_1 = (0, -wB, 0)`

`B_2 = ((sqrt(3) / 2) wB, (1 / 2) wB, 0)`

`B_3 = (-(sqrt(3) / 2) wB, (1 / 2) wB, 0)`

## 9. Platform Point Coordinate Note
platform center를 `(x, y, z)`라고 두고, platform triangle `sP`가 base와 평행하며 arm index 순서를 따른다고 보면 `P_1`은 `-y` 방향 vertex로 두는 해석이 가장 자연스럽다.

따라서 1차 메모 기준으로:

`P_1 = (x, y - uP, z)`

로 둘 수 있다.

해석:
- `uP`는 platform center에서 vertex까지의 거리다
- `P_1`은 `B_1`에 연결되는 platform vertex다
- arm 1이 `-y` 방향 쪽에 대응하므로 `P_1`도 같은 방향 vertex로 둔다

같은 해석을 쓰면 대칭점은 참고 수준으로 다음처럼 적을 수 있다.

`P_2 = (x + (sqrt(3) / 2) uP, y + (1 / 2) uP, z)`

`P_3 = (x - (sqrt(3) / 2) uP, y + (1 / 2) uP, z)`

이때 arm 1 길이 제약식의 출발점은:

`|P_1 - J_1(theta_1)|^2 = l^2`

즉,

`|(x, y - uP, z) - (0, -wB - L cos(theta_1), -L sin(theta_1))|^2 = l^2`

가 된다.

이 식을 전개하면 arm 1의 `E_1`, `F_1`, `G_1` 형태를 도출할 수 있다.

## 10. Practical Mapping For This Project
현재 프로젝트에 바로 연결되는 최소 해석은 아래와 같다.

- 입력 position은 `base_frame` 기준 `mm`
- 출력 angle은 `deg`
- 실제 수식 전개는 내부적으로 radian을 사용하는 편이 안전하다
- `B_i`는 `wB` 기준, `P_i`는 `uP` 기준으로 좌표식을 통일하는 편이 해석상 가장 단순하다
- 각 arm의 수식은 arm 1 기준 식을 만든 뒤, `120 deg` 회전 대칭으로 arm 2, arm 3에 확장하는 방식이 유력하다
- 또는 각 arm별 local plane으로 좌표를 변환한 뒤 같은 식을 재사용하는 방식도 가능하다

현 단계에서 아직 미정인 부분:
- arm별 local plane 정의
- `theta_cmd`가 실제 모터 구동축 기준과 정확히 어떻게 연결되는지
- arm 2, arm 3의 전개 방식
- `P_i` 표현을 `uP` 기준으로 고정할지, 회전 행렬 기반 일반식으로 바꿀지

## 11. Remaining Open Items
현재 문서는 구조 메모다. 아래 항목은 아직 별도 확정이 필요하다.

- `theta_cmd`와 실제 모터 구동축/드라이버 명령의 정확한 연결
- `downward-working branch`의 구현 판정식을 더 엄밀하게 둘지 여부
- 임시 working range `0 deg <= theta_i <= 90 deg`의 최종 하드웨어 범위 갱신
- FK 기반 역검증 절차

## 12. Arm 1 Expansion Note
arm 1 기준 좌표식은 다음과 같다.

`P_1 = (x, y - uP, z)`

`J_1(theta_1) = (0, -wB - L cos(theta_1), -L sin(theta_1))`

따라서 차 벡터는:

`P_1 - J_1(theta_1) = (x, y - uP + wB + L cos(theta_1), z + L sin(theta_1))`

길이 제약식:

`|P_1 - J_1(theta_1)|^2 = l^2`

을 그대로 쓰면:

`x^2 + (y - uP + wB + L cos(theta_1))^2 + (z + L sin(theta_1))^2 = l^2`

여기서

`A_1 = y - uP + wB`

로 두면 식은 더 간단해진다.

`x^2 + (A_1 + L cos(theta_1))^2 + (z + L sin(theta_1))^2 = l^2`

전개하면:

`x^2 + A_1^2 + 2 A_1 L cos(theta_1) + L^2 cos^2(theta_1) + z^2 + 2 z L sin(theta_1) + L^2 sin^2(theta_1) = l^2`

`cos^2(theta_1) + sin^2(theta_1) = 1`

을 쓰면:

`2 A_1 L cos(theta_1) + 2 z L sin(theta_1) + x^2 + A_1^2 + z^2 + L^2 - l^2 = 0`

따라서 arm 1에 대해:

`E_1 = 2 L (y - uP + wB)`

`F_1 = 2 L z`

`G_1 = x^2 + (y - uP + wB)^2 + z^2 + L^2 - l^2`

로 둘 수 있고, 최종 형태는:

`E_1 cos(theta_1) + F_1 sin(theta_1) + G_1 = 0`

가 된다.

이제 arm 1의 `t = tan(theta_1 / 2)` 치환은 바로 이어서 적용 가능하다.

## 13. Arm 1 Half-Angle Note
반각 치환:

`t_1 = tan(theta_1 / 2)`

을 사용하면

`cos(theta_1) = (1 - t_1^2) / (1 + t_1^2)`

`sin(theta_1) = 2 t_1 / (1 + t_1^2)`

가 된다.

이를

`E_1 cos(theta_1) + F_1 sin(theta_1) + G_1 = 0`

에 대입하면:

`E_1 (1 - t_1^2) / (1 + t_1^2) + F_1 (2 t_1) / (1 + t_1^2) + G_1 = 0`

양변에 `(1 + t_1^2)`를 곱해 정리하면:

`(G_1 - E_1) t_1^2 + 2 F_1 t_1 + (E_1 + G_1) = 0`

따라서 arm 1의 `t_1` 해는:

`t_1 = (-F_1 ± sqrt(E_1^2 + F_1^2 - G_1^2)) / (G_1 - E_1)`

로 쓸 수 있다.

최종 각도 복원식은:

`theta_1 = 2 atan(t_1)`

이다.

## 14. IK Root Selection Rule
역기구학에서 각 arm `i`에 대해 `2atan(t)` 기반 해를 계산할 때, `+/-` 두 해는 아래 규칙으로 선택한다.

1. 판별식 `E_i^2 + F_i^2 - G_i^2`가 `0`보다 작으면 해당 목표점은 도달 불가능으로 보고 `reject`한다.
2. 판별식을 통과하면 두 해 `theta_i^(+)`, `theta_i^(-)`를 계산한다.
3. 현재 단계의 임시 working range인 `0 deg <= theta_i <= 90 deg`를 만족하는 해만 유효 후보로 남긴다. 최종 `theta_min`, `theta_max`는 기구 파라미터와 하드웨어 제약 확정 후 갱신한다.
4. `theta_i = 0 deg`가 upper arm이 `base plane`에 놓인 자세이고, `theta_i = +90 deg`가 upper arm이 workspace direction인 `-z` 방향과 평행한 자세라는 정의에 따라, upper arm이 workspace 방향으로 내려가는 `downward-working branch`에 속하는 해만 남긴다.
5. 유효 후보가 없으면 `reject`한다.
6. 유효 후보가 하나면 그 해를 선택한다.
7. 유효 후보가 둘이면 이전 시점 각도 `previous_theta_i`와 가장 가까운 해를 선택한다.
8. 초기 시점처럼 `previous_theta_i`가 없는 경우에는 기본 branch 우선순위에 따라 `downward-working branch`의 해를 선택한다.

## 15. Symmetry Expansion Note
세 arm은 `base_frame`에서 `120 deg` 회전 대칭을 이룬다고 본다.
각 arm의 base outward 방향 단위벡터를 다음처럼 둔다.

`e_1 = (0, -1)`

`e_2 = ((sqrt(3) / 2), (1 / 2))`

`e_3 = (-(sqrt(3) / 2), (1 / 2))`

그러면 horizontal plane에서:

`B_i = wB e_i`

`P_i = (x, y) + uP e_i`

로 일반화할 수 있다.

또한 upper arm end point는:

`J_i(theta_i) = (wB + L cos(theta_i)) e_i + ( -L sin(theta_i) ) k`

로 쓸 수 있다. 여기서 `k`는 global `+z` 방향 단위벡터이며, 실제 좌표의 `z` 성분은 workspace direction이 `-z`이므로 음수 부호를 가진다.

즉 3차원 좌표로 쓰면:

- `J_1(theta_1) = (0, -wB - L cos(theta_1), -L sin(theta_1))`
- `J_2(theta_2) = ((sqrt(3) / 2)(wB + L cos(theta_2)), (1 / 2)(wB + L cos(theta_2)), -L sin(theta_2))`
- `J_3(theta_3) = (-(sqrt(3) / 2)(wB + L cos(theta_3)), (1 / 2)(wB + L cos(theta_3)), -L sin(theta_3))`

그리고 platform connection point는:

- `P_1 = (x, y - uP, z)`
- `P_2 = (x + (sqrt(3) / 2) uP, y + (1 / 2) uP, z)`
- `P_3 = (x - (sqrt(3) / 2) uP, y + (1 / 2) uP, z)`

## 16. Generalized EFG Note
horizontal target position을 `r = (x, y)`라고 두고, arm `i`의 outward unit vector를 `e_i`라 하면

`p_i = r · e_i`

로 둘 수 있다.

길이 제약식

`|P_i - J_i(theta_i)|^2 = l^2`

을 같은 방식으로 전개하면

`E_i cos(theta_i) + F_i sin(theta_i) + G_i = 0`

형태가 유지되며, 일반형은 다음처럼 쓸 수 있다.

`E_i = -2 L (p_i + uP - wB)`

`F_i = 2 L z`

`G_i = x^2 + y^2 + (uP - wB)^2 + 2 (uP - wB) p_i + z^2 + L^2 - l^2`

arm별로 쓰면:

`p_1 = -y`

`p_2 = (sqrt(3) / 2) x + (1 / 2) y`

`p_3 = -(sqrt(3) / 2) x + (1 / 2) y`

따라서

`E_1 = 2 L (y - uP + wB)`

`E_2 = 2 L (-(sqrt(3) / 2) x - (1 / 2) y - uP + wB)`

`E_3 = 2 L ((sqrt(3) / 2) x - (1 / 2) y - uP + wB)`

`F_1 = F_2 = F_3 = 2 L z`

`G_1 = x^2 + (y - uP + wB)^2 + z^2 + L^2 - l^2`

`G_2 = x^2 + y^2 + (uP - wB)^2 + 2 (uP - wB) ((sqrt(3) / 2) x + (1 / 2) y) + z^2 + L^2 - l^2`

`G_3 = x^2 + y^2 + (uP - wB)^2 + 2 (uP - wB) (-(sqrt(3) / 2) x + (1 / 2) y) + z^2 + L^2 - l^2`

가 된다.

arm 1 식은 이 일반식의 특수한 경우다.
