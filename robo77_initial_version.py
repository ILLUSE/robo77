import random

class Robo77:
    def __init__(self, players, is_computer):
        self.players = players  # 플레이어 수
        self.is_computer = is_computer  # 컴퓨터 플레이어 여부 리스트
        self.current_total = 0  # 현재 총합
        self.deck = self.create_deck()  # 새로운 카드 구성으로 덱 생성
        random.shuffle(self.deck)  # 덱 섞기
        self.hands = {i: [self.draw_card() for _ in range(5)] for i in range(players)}  # 각 플레이어에게 카드 5장씩 분배

    def create_deck(self):
        deck = []
        # 2~9는 3장씩, 10은 8장
        for i in range(2, 10):
            deck.extend([i] * 3)
        deck.extend([10] * 8)

        # 특수 숫자 카드
        special_numbers = [0, 11, 22, 33, 44, 55, 66, 76]
        for num in special_numbers:
            deck.append(num)

        # 특수 기능 카드
        deck.extend([-10] * 4)  # -10 카드 4장
        deck.extend(['*2'] * 4)  # *2 카드 4장
        deck.extend(['reverse'] * 5)  # 방향 전환 카드 5장

        return deck

    def draw_card(self):
        return self.deck.pop() if self.deck else None

    def computer_choose_card(self, player):
        best_card = None
        best_total = -float('inf')

        for card in self.hands[player]:
            # 각 카드에 따른 새로운 총합 계산
            if card == '*2':
                new_total = self.current_total * 2
            elif card == -10:
                new_total = self.current_total - 10
            elif card == 'reverse':
                new_total = self.current_total
            else:
                new_total = self.current_total + card

            # 77 이하, 11의 배수가 아님, 가장 높은 총합이 되도록 최적 카드 선택(greedy alghorithm)
            if new_total <= 77 and new_total % 11 != 0 and new_total > best_total:
                best_card = card
                best_total = new_total

        # 가능한 카드 중 11의 배수를 피하지 못할 경우, 가장 적은 영향을 주는 카드를 선택
        if best_card is None:
            best_card = min(self.hands[player], key=lambda x: abs(self.current_total + (x if isinstance(x, int) else 0) - 77))

        return best_card

    def play_turn(self, player, direction):
        print(f"\n플레이어 {player + 1}의 차례입니다.")
        print(f"현재 총합: {self.current_total}")
        print(f"플레이어 {player + 1}의 손: {[str(card) for card in self.hands[player]]}")

        if self.is_computer[player]:  # 컴퓨터 플레이어의 경우
            card = self.computer_choose_card(player)
            print(f"컴퓨터가 {card} 카드를 냈습니다.")
        else:  # 인간 플레이어의 경우
            # 게임 종료 코드 입력 시 즉시 종료
            user_input = input("내고 싶은 카드를 선택하세요 (게임 종료: -1): ")
            if user_input == "-1":
                print("게임을 종료합니다.")
                return False, direction

            try:
                card = int(user_input) if user_input.isdigit() or user_input == '-10' else user_input
            except ValueError:
                print("잘못된 입력입니다. 다시 선택하세요.")
                return self.play_turn(player, direction)

            if card not in self.hands[player]:
                print("잘못된 카드입니다. 다시 선택하세요.")
                return self.play_turn(player, direction)

        # 특수 카드 적용
        if card == -10:
            self.current_total -= 10
            print(f"플레이어 {player + 1}가 -10을 사용하여 총합이 {self.current_total}이 되었습니다.")
        elif card == '*2':
            self.current_total *= 2
            print(f"플레이어 {player + 1}가 *2를 사용하여 총합이 {self.current_total}이 되었습니다.")
        elif card == 'reverse':
            direction *= -1  # reverse 카드가 낼 때만 방향 변경
            print(f"플레이어 {player + 1}가 방향 전환 카드를 사용했습니다. 다음 플레이어의 차례가 반대 방향으로 바뀝니다.")
        else:
            # 일반 카드 사용
            self.current_total += card
            print(f"플레이어 {player + 1}가 {card}을(를) 내서 총합이 {self.current_total}이 되었습니다.")

        # 11의 배수일 때 패배 조건
        if self.current_total > 0 and self.current_total % 11 == 0:
            print(f"현재 총합 {self.current_total}가 11의 배수가 되어 플레이어 {player + 1}가 패배했습니다! 게임 종료.")
            return False, direction

        # 총합이 77을 초과할 때 패배 조건
        if self.current_total > 77:
            print(f"플레이어 {player + 1}가 패배했습니다! 게임 종료.")
            return False, direction

        # 카드 사용 후 즉시 한 장 추가
        self.hands[player].remove(card)
        new_card = self.draw_card()
        if new_card:
            self.hands[player].append(new_card)
            print(f"플레이어 {player + 1}가 새로운 카드를 뽑았습니다: {new_card}")

        return True, direction

    def start_game(self):
        turn = 0
        direction = 1  # 방향 (1: 정방향, -1: 역방향)
        while True:
            player = turn % self.players
            continue_game, direction = self.play_turn(player, direction)
            if not continue_game:
                break
            turn += direction

# 게임 시작
num_players = int(input("플레이어 수를 입력하세요 (2 이상): "))
computer_player_index = int(input("컴퓨터 플레이어의 인덱스를 입력하세요 (0부터 시작): "))
is_computer = [i == computer_player_index for i in range(num_players)]
game = Robo77(num_players, is_computer)
game.start_game()