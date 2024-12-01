# version 2 : 게임 화면 구현
import pygame
import random
import sys

# Initialize Pygame
pygame.init()

# Screen dimensions and settings
WIDTH, HEIGHT = 800, 600
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 120, 215)
RED = (215, 0, 0)

# Initialize screen
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Robo77")

# Font settings
font = pygame.font.Font(None, 25)
large_font = pygame.font.Font(None, 48)

# Card dimensions
CARD_WIDTH, CARD_HEIGHT = 80, 120

# Game variables
current_total = 0
user_hand = []
computer_hand = []
remaining_cards = []
user_life_chips = 3
computer_life_chips = 3
user_turn = True
game_message = "Your turn!"
computer_played_card = None
user_drawn_card = None
computer_drawn_card = None
special_cards = ["reverse", "-10", "0", "76", "*2"]
direction = 1  # 1: Clockwise, -1: Counter-clockwise
cards_per_row = 7  # 한 줄에 표시할 카드 수

# Create deck
def create_deck():
    deck = []
    for i in range(2, 10):
        deck.extend([i] * 3)
    deck.extend([10] * 8)
    deck.extend(["reverse"] * 5)
    deck.extend([0] * 4)
    deck.extend(["*2"] * 4)
    deck.extend([-10] * 4)
    deck.extend([11, 22, 33, 44, 55, 66, 76])
    random.shuffle(deck)
    return deck

# Draw text
def draw_text(text, font, color, x, y):
    text_surface = font.render(text, True, color)
    screen.blit(text_surface, (x, y))

# Draw card
def draw_card(card, x, y, clickable=True):
    pygame.draw.rect(screen, BLUE if clickable else RED, (x, y, CARD_WIDTH, CARD_HEIGHT), border_radius=10)
    text_color = WHITE if clickable else BLACK
    draw_text(str(card), font, text_color, x + CARD_WIDTH // 3, y + CARD_HEIGHT // 3)

# Draw life chips
def draw_life_chips(x, y, life_chips):
    for i in range(life_chips):
        pygame.draw.circle(screen, RED, (x + i * 30, y), 10)

# Draw user hand with multiple rows
def draw_user_hand():
    global cards_per_row
    row_offset = 0  # 줄 바꿈을 위한 y 좌표
    for i, card in enumerate(user_hand):
        # 줄바꿈: i가 cards_per_row의 배수가 되면 다음 줄로 이동
        if i > 0 and i % cards_per_row == 0:
            row_offset += CARD_HEIGHT + 20  # 카드 높이 + 간격만큼 줄바꿈

        # 카드 위치 계산
        x = 50 + (i % cards_per_row) * (CARD_WIDTH + 20)  # 한 줄에 cards_per_row 개
        y = HEIGHT - CARD_HEIGHT - 40 - row_offset  # 아래에서 줄바꿈 적용

        draw_card(card, x, y)

# Initialize game
def initialize_game():
    global user_hand, computer_hand, deck, current_total, user_turn, game_message, direction, computer_played_card, user_drawn_card, computer_drawn_card
    deck = create_deck()
    user_hand = [deck.pop() for _ in range(5)]
    computer_hand = [deck.pop() for _ in range(5)]
    current_total = 0
    user_turn = True
    game_message = "Your turn!"
    direction = 1
    computer_played_card = None
    user_drawn_card = None
    computer_drawn_card = None

# Apply card effect
def apply_card(card, player):
    global current_total, deck, game_message, user_drawn_card, computer_drawn_card

    # special_cards
    if isinstance(card, int):
        current_total += card
    elif card == 76:
        if current_total <= 0:  # 총합이 0 이하일 때만 사용 가능
            current_total = 76
            game_message = f"{'Computer' if player == 'computer' else 'You'} played 76. Total is now 76!"
        else:
            game_message = "76 can only be played at the start or when total is 0 or below."
            return False  # 카드 무효화
    elif card == "reverse":
        global direction
        direction *= -1
    elif card == "-10":
        current_total -= 10
    elif card == "0":
        pass
    elif card == "*2":  # 상대방에게 카드 2장 추가
        target_hand = computer_hand if player == "user" else user_hand
        for _ in range(2):
            if deck:
                target_hand.append(deck.pop())
        game_message = f"{'Computer' if player == 'computer' else 'You'} played *2. Opponent drew 2 cards!"

    # 카드 더미가 비었는지 확인
    if not deck:
        game_message = "Deck is empty! No more cards to draw."
        return True

    # 카드 더미에서 한 장 가져오기
    if player == "user" and deck:
        user_drawn_card = deck.pop()
        user_hand.append(user_drawn_card)
        game_message = f"You drew {user_drawn_card} from the deck."
    elif player == "computer" and deck:
        computer_drawn_card = deck.pop()
        computer_hand.append(computer_drawn_card)
        game_message = f"Computer drew a card from the deck."

    return True

# Computer play
def computer_play():
    global user_turn, game_message, computer_played_card

    best_card = None
    for card in computer_hand:
        if isinstance(card, int):
            new_total = current_total + card
        elif card == "-10":
            new_total = current_total - 10
        else:
            new_total = current_total

        if new_total <= 77 and new_total % 11 != 0:
            best_card = card
            break

    if best_card is None:
        best_card = computer_hand[0]

    computer_hand.remove(best_card)
    computer_played_card = best_card
    apply_card(best_card, "computer")
    game_message = f"Computer played {computer_played_card}."

    if not check_game_over(False):
        pygame.time.set_timer(pygame.USEREVENT + 1, 1000)  # 1초 대기 후 다음 메시지

# Check game over conditions
def check_game_over(is_user):
    global user_life_chips, computer_life_chips, game_message

    if current_total > 77:
        if is_user:
            user_life_chips -= 1
            if user_life_chips == 0:  # 생명칩이 모두 소진되었으면 게임 종료
                game_message = "Game Over! Computer wins!"
                return True
            else:
                game_message = "You lose a life chip! Round over."
        else:
            computer_life_chips -= 1
            if computer_life_chips == 0:  # 생명칩이 모두 소진되었으면 게임 종료
                game_message = "Game Over! You win!"
                return True
            else:
                game_message = "Computer loses a life chip! Round over."
        initialize_game()  # 생명 칩이 남아있으면 라운드 재시작
        return False

    if current_total % 11 == 0 and current_total > 0:
        if is_user:
            user_life_chips -= 1
            if user_life_chips == 0:  # 생명칩이 모두 소진되었으면 게임 종료
                game_message = "Game Over! Computer wins!"
                return True
            else:
                game_message = "You lose a life chip! It's 11's multiple!"
        else:
            computer_life_chips -= 1
            if computer_life_chips == 0:  # 생명칩이 모두 소진되었으면 게임 종료
                game_message = "Game Over! You win!"
                return True
            else:
                game_message = "Computer loses a life chip! It's 11's multiple!"
        initialize_game()  # 생명 칩이 남아있으면 라운드 재시작
        return False

    return False


# Main game loop
def main():
    global user_turn, game_message

    initialize_game()

    running = True
    while running:
        screen.fill(WHITE)

        # Draw current total
        draw_text(f"Current Total: {current_total}", large_font, BLACK, WIDTH // 2 - 150, 50)

        # Draw user life chips
        draw_text("User Life Chips:", font, BLACK, 50, 120)
        draw_life_chips(250, 130, user_life_chips)

        # Draw computer life chips
        draw_text("Computer Life Chips:", font, BLACK, 50, 170)
        draw_life_chips(250, 180, computer_life_chips)

        # Draw game message
        message_color = RED if user_turn else BLUE
        draw_text(game_message, font, message_color, WIDTH // 2 - 150, HEIGHT // 2)

        # Draw user hand
        draw_user_hand()  # 사용자 카드 줄바꿈 표시

        # Display computer's last played card
        if computer_played_card is not None:
            draw_text(f"Computer's Last Card: {computer_played_card}", font, BLACK, WIDTH // 2 - 150, HEIGHT // 2 + 50)

        # Display user-drawn card
        if user_drawn_card is not None:
            draw_text(f"You drew: {user_drawn_card}", font, BLACK, 50, HEIGHT - CARD_HEIGHT - 80)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN and user_turn:
                x, y = pygame.mouse.get_pos()
                for i, card in enumerate(user_hand):
                    card_x = 50 + (i % cards_per_row) * (CARD_WIDTH + 20)
                    card_y = HEIGHT - CARD_HEIGHT - 40 - (i // cards_per_row) * (CARD_HEIGHT + 20)
                    if card_x <= x <= card_x + CARD_WIDTH and card_y <= y <= card_y + CARD_HEIGHT:
                        user_hand.remove(card)
                        apply_card(card, "user")
                        if check_game_over(True):
                            running = False
                        else:
                            if not deck:
                                game_message = "Deck is empty! No more cards to draw."
                            user_turn = False
                            game_message = "Computer's turn!"
                            pygame.time.set_timer(pygame.USEREVENT, 1000)

            # 컴퓨터가 카드를 낸 후 처리
            if event.type == pygame.USEREVENT:
                pygame.time.set_timer(pygame.USEREVENT, 0)
                computer_play()

            # 컴퓨터가 카드를 가져오는 메시지
            if event.type == pygame.USEREVENT + 1:
                pygame.time.set_timer(pygame.USEREVENT + 1, 0)
                if computer_drawn_card is not None:
                    game_message = "Computer drew a card."
                pygame.time.set_timer(pygame.USEREVENT + 2, 1000)  # 1초 후 사용자 턴 시작

            # 사용자 턴 시작 메시지
            if event.type == pygame.USEREVENT + 2:
                pygame.time.set_timer(pygame.USEREVENT + 2, 0)
                user_turn = True
                game_message = "Your turn!"

        pygame.display.flip()

        # 게임 종료 메시지 표시 후 종료
        if not running:
            if user_life_chips == 0:
                game_message = "Game Over! Computer wins!"
            elif computer_life_chips == 0:
                game_message = "Game Over! You win!"
            draw_text(game_message, large_font, RED, WIDTH // 2 - 150, HEIGHT // 2 + 100)
            pygame.display.flip()
            pygame.time.wait(3000)  # 3초 대기 후 종료
            pygame.quit()
            sys.exit()


if __name__ == "__main__":
    main()
