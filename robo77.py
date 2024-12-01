# ver 4 : 이미지 로드 함수 추가, 카드 이미지 로드 및 표시 함수 추가, 특수 카드 이미지 로드 및 표시 함수 추가, 이미지 크기 조정, 이미지 로드 확인용 출력 추가
import pygame
import random
import sys
import os

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
warning_font = pygame.font.Font(None, 48)
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

# 이미지 경로 설정
IMAGE_PATH = os.path.join('robo77-images')

card_names = [
    '1', '2', '3', '4', '5', '6', '7', '8', '9', '10', 
    '11', '22', '33', '44', '55', '66', '76', 
    'reverse', '0', 'x2', '-10'
]

# 이미지 로드 함수 추가
def load_images():
    images = {}
    try:
        print(f"현재 이미지 경로: {IMAGE_PATH}")  # 경로 확인용 출력
        
        # 카드 이미지 로드
        for card_name in card_names:
            card_path = os.path.join(IMAGE_PATH, f'card_{card_name}.png')
            if os.path.exists(card_path):
                print(f"카드 이미지 로드 성공: {card_path}")  # 성공한 이미지 로드 확인
                images[card_name] = pygame.image.load(card_path)
            else:
                print(f"카드 이미지 없음: {card_path}")  # 없는 이미지 파일 확인
        
        # 특수 카드 이미지 로드
        special_cards = {
            'reverse': 'card_reverse.png',
            '0': 'card_0.png',
            '*2': 'card_x2.png',
            '-10': 'card_-10.png',
            'chip': 'chip.png',
            'layout': 'layout.png'
        }
        
        for key, filename in special_cards.items():
            file_path = os.path.join(IMAGE_PATH, filename)
            if os.path.exists(file_path):
                print(f"특수 카드 이미지 로드 성공: {file_path}")
                images[key] = pygame.image.load(file_path)
            else:
                print(f"특수 카드 이미지 없음: {file_path}")
        
        # 이미지 크기 조정
        for key in images:
            if key != 'layout':  # 배경 제외
                images[key] = pygame.transform.scale(images[key], (CARD_WIDTH, CARD_HEIGHT))
                
        print(f"로드된 총 이미지 수: {len(images)}")  # 총 로드된 이미지 수 확인
        
    except Exception as e:
        print(f"이미지 로드 중 오류 발생: {e}")
    return images

# Draw text
def draw_text(text, font, color, x, y):
    text_surface = font.render(text, True, color)
    screen.blit(text_surface, (x, y))

# Draw card
def draw_card(card, x, y, clickable=True):
    if not hasattr(draw_card, 'images'):
        draw_card.images = load_images()
    
    card_str = str(card)
    if card_str in draw_card.images:
        if clickable:
            screen.blit(draw_card.images[card_str], (x, y))
        else:
            # 비활성화된 카드는 약간 어둡게 표시
            dark_card = draw_card.images[card_str].copy()
            dark_card.fill((100, 100, 100), special_flags=pygame.BLEND_RGBA_MULT)
            screen.blit(dark_card, (x, y))
    else:
        # 이미지가 없는 경우 기존 방식으로 표시
        pygame.draw.rect(screen, BLUE if clickable else RED, (x, y, CARD_WIDTH, CARD_HEIGHT), border_radius=10)
        text_color = WHITE if clickable else BLACK
        draw_text(str(card), font, text_color, x + CARD_WIDTH // 3, y + CARD_HEIGHT // 3)

# Draw life chips with animation support
def draw_life_chips(x, y, life_chips):
    if not hasattr(draw_life_chips, 'chip_image'):
        draw_life_chips.chip_image = load_images().get('chip')
    
    # 애니메이션 처리
    for anim in life_chip_animations[:]:
        anim['scale'] -= 0.1
        anim['alpha'] -= 25
        
        if draw_life_chips.chip_image:
            chip_surface = pygame.transform.scale(
                draw_life_chips.chip_image,
                (int(20 * anim['scale']), int(20 * anim['scale']))
            )
            chip_surface.set_alpha(anim['alpha'])
            screen.blit(chip_surface, (anim['x'], anim['y']))
        
        if anim['alpha'] <= 0:
            life_chip_animations.remove(anim)
    
    # 현재 라이프 칩 표시
    if draw_life_chips.chip_image:
        for i in range(life_chips):
            screen.blit(pygame.transform.scale(draw_life_chips.chip_image, (20, 20)), 
                       (x + i * 30, y - 10))
    else:
        # 이미지가 없는 경우 기존 방식으로 표시
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

# Create deck 함수 수정
def create_deck():
    deck = []
    # 일반 숫자 카드 (2-9)
    for i in range(2, 10):
        deck.extend([str(i)] * 3)  # 각 숫자당 3장씩
    
    # 10 카드
    deck.extend(['10'] * 8)
    
    # 특수 카드
    deck.extend(['reverse'] * 5)  # reverse 카드 5장
    deck.extend(['0'] * 4)        # 0 카드 4장
    deck.extend(['*2'] * 4)       # *2 카드 4장
    deck.extend(['-10'] * 4)      # -10 카드 4장
    
    # 11의 배수 카드
    deck.extend(['11', '22', '33', '44', '55', '66', '76'])
    
    random.shuffle(deck)
    return deck

# apply_card 함수도 수정이 필요합니다
def apply_card(card, player):
    global current_total, deck, game_message, user_drawn_card, computer_drawn_card

    # 카드 효과 적용
    if card.isdigit() or (card.startswith('-') and card[1:].isdigit()):
        current_total += int(card)
    elif card == '76':
        if current_total <= 0:
            current_total = 76
            game_message = f"{'Computer' if player == 'computer' else 'You'} played 76. Total is now 76!"
        else:
            game_message = "76 can only be played at the start or when total is 0 or below."
            return False
    elif card == "reverse":
        global direction
        direction *= -1
    elif card == "*2":  # *2 카드
        current_total *= 2
        game_message = f"{'Computer' if player == 'computer' else 'You'} played *2. Total is now {current_total}!"
    
    # *2 카드는 상대가 *2 내면 내가 2장을 내고 2장을 드로우함
    # elif card == "*2":
    #     target_hand = computer_hand if player == "user" else user_hand
    #     for _ in range(2):
    #         if deck:
    #             target_hand.append(deck.pop())
    #     game_message = f"{'Computer' if player == 'computer' else 'You'} played *2. Opponent drew 2 cards!"

    # 카드 드로우 처리
    if deck:
        if player == "user":
            user_drawn_card = deck.pop()
            user_hand.append(user_drawn_card)
            game_message = f"You drew {user_drawn_card} from the deck."
        else:
            computer_drawn_card = deck.pop()
            computer_hand.append(computer_drawn_card)
            game_message = f"Computer drew a card from the deck."
    else:
        game_message = "Deck is empty! No more cards to draw."

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
    game_images = load_images()
    
    running = True
    while running:
        # 배경 이미지 그리기
        if 'layout' in game_images:
            screen.blit(game_images['layout'], (0, 0))
        else:
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
        message_color = WHITE if user_turn else BLUE
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