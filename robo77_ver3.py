# version 3: 게임 라운드 종료 시 승패 여부 확인 및 애니메이션 효과 추가
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
GRAY = (200, 200, 200)

# Initialize screen
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Robo77")

# Font settings
font = pygame.font.Font(None, 25)
large_font = pygame.font.Font(None, 48)
warning_font = pygame.font.Font(None, 64)
consensus_font = pygame.font.Font(None, 80)

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

# Life chip animation variables
life_chip_animations = []
consensus_animation = None

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

# Draw life chips with animation support
def draw_life_chips(x, y, life_chips):
    global life_chip_animations
   
    # Process and draw life chip animations
    for anim in life_chip_animations[:]:
        anim['scale'] -= 0.1
        anim['alpha'] -= 25
       
        # Create a surface with alpha transparency
        chip_surface = pygame.Surface((20, 20), pygame.SRCALPHA)
        pygame.draw.circle(chip_surface, (*RED, anim['alpha']), (10, 10), int(10 * anim['scale']))
       
        # Draw the animated chip
        screen.blit(chip_surface, (anim['x'], anim['y']))
       
        # Remove animation when fully transparent
        if anim['alpha'] <= 0:
            life_chip_animations.remove(anim)
   
    # Draw current life chips
    for i in range(life_chips):
        pygame.draw.circle(screen, RED, (x + i * 30, y), 10)

# Draw warning message
def draw_warning_message(message, duration=2000):
    warning_surface = warning_font.render(message, True, RED)
    warning_rect = warning_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2))
   
    # Fade in and out effect
    for alpha in range(0, 256, 25):
        screen.fill(WHITE)
        warning_surface.set_alpha(alpha)
        screen.blit(warning_surface, warning_rect)
        pygame.display.flip()
        pygame.time.delay(50)
   
    pygame.time.delay(duration)
   
    for alpha in range(255, 0, -25):
        screen.fill(WHITE)
        warning_surface.set_alpha(alpha)
        screen.blit(warning_surface, warning_rect)
        pygame.display.flip()
        pygame.time.delay(50)

# Draw consensus emphasis animation
def trigger_consensus_animation(message):
    global consensus_animation
    consensus_animation = {
        'message': message,
        'alpha': 0,
        'scale': 1.0,
        'duration': 120  # Total animation frames
    }

# Render consensus animation
def render_consensus_animation(screen):
    global consensus_animation
   
    if consensus_animation:
        # Fade in
        if consensus_animation['alpha'] < 255:
            consensus_animation['alpha'] += 20
            consensus_animation['scale'] -= 0.02

        consensus_surface = consensus_font.render(
            consensus_animation['message'],
            True,
            RED
        )
       
        # Apply alpha and scale
        consensus_surface.set_alpha(consensus_animation['alpha'])
       
        # Scale surface
        scaled_width = int(consensus_surface.get_width() * consensus_animation['scale'])
        scaled_height = int(consensus_surface.get_height() * consensus_animation['scale'])
        scaled_surface = pygame.transform.scale(consensus_surface, (scaled_width, scaled_height))
       
        # Position at center
        rect = scaled_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        screen.blit(scaled_surface, rect)
       
        # Decrement duration
        consensus_animation['duration'] -= 1
       
        # Reset when animation complete
        if consensus_animation['duration'] <= 0:
            consensus_animation = None

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
    global user_hand, computer_hand, deck, current_total, user_turn, game_message, direction, computer_played_card, user_drawn_card, computer_drawn_card, life_chip_animations, consensus_animation
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
    life_chip_animations = []
    consensus_animation = None

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

# 승패 여부 출력
def check_game_over(is_user):
    global user_life_chips, computer_life_chips, game_message, life_chip_animations, consensus_animation

    if current_total > 77:
        if is_user:
            life_chip_animations.append({
                'x': 250 + (user_life_chips - 1) * 30,
                'y': 120,
                'scale': 1.0,
                'alpha': 255
            })
            # 플레이어가 합이 77이 넘어서 지는 경우
            user_life_chips -= 1
            trigger_consensus_animation("OVER 77!")
           
            if user_life_chips == 0:
                game_message = "Game Over! Computer wins!"
                draw_warning_message("GAME OVER! YOU LOSE!")
                return True
            else:
                game_message = "You lost a life chip! Over 77!"
                draw_warning_message("Over 77! Your Life Chip Lost!")
        else:
            # 컴퓨터가 합이 77이 넘어서 지는 경우
            life_chip_animations.append({
                'x': 250 + (computer_life_chips - 1) * 30,
                'y': 170,
                'scale': 1.0,
                'alpha': 255
            })
           
            computer_life_chips -= 1
            trigger_consensus_animation("COMPUTER OVER 77!")
           
            if computer_life_chips == 0:
                game_message = "Game Over! You win!"
                draw_warning_message("Congratulations! YOU WIN!")
                return True
            else:
                game_message = "Computer lost a life chip! Over 77!"
                draw_warning_message("Over 77! Computer Life Chip Lost!")
        initialize_game()
        return False

    if current_total % 11 == 0 and current_total > 0:
        if is_user:
            # 플레이어가 합이 11의 배수여서 지는 경우
            life_chip_animations.append({
                'x': 250 + (user_life_chips - 1) * 30,
                'y': 120,
                'scale': 1.0,
                'alpha': 255
            })
           
            user_life_chips -= 1
            trigger_consensus_animation("MULTIPLE OF 11!")
           
            if user_life_chips == 0:
                game_message = "Game Over! Computer wins!"
                draw_warning_message("GAME OVER! YOU LOSE!")
                return True
            else:
                game_message = "You lost a life chip! Multiple of 11!"
                draw_warning_message("Multiple of 11! Your Life Chip lost!")
        else:
            # 컴퓨터가 합이 11의 배수여서 지는 경우
            life_chip_animations.append({
                'x': 250 + (computer_life_chips - 1) * 30,
                'y': 170,
                'scale': 1.0,
                'alpha': 255
            })
           
            computer_life_chips -= 1
            trigger_consensus_animation("COMPUTER MULTIPLE OF 11!")
           
            if computer_life_chips == 0:
                game_message = "Game Over! You win!"
                draw_warning_message("Congratulations! YOU WIN!")
                return True
            else:
                game_message = "Computer lost a life chip! Multiple of 11!"
                draw_warning_message("Multiple of 11! Computer Life Chip Lost!")
        initialize_game()
        return False

    return False

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
        draw_user_hand()  # 사용자 카드 줄바
        # Render consensus animation
        render_consensus_animation(screen)

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
                user_turn = True
                game_message = "Your turn!"

        pygame.display.flip()
        pygame.time.Clock().tick(60)

# Run the game
if __name__ == "__main__":
    main()