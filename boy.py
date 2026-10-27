from pico2d import (
    load_image, get_canvas_width,
    SDL_KEYDOWN, SDL_KEYUP,
    SDLK_LEFT, SDLK_RIGHT, SDLK_SPACE
)
from transitions import Machine
import time


class Boy:
    def __init__(self):
        self.x, self.y = 400, 90
        self.frame = 0
        self.face_dir = 1
        self.speed = 5

        self.left_pressed = False
        self.right_pressed = False

        self.image = load_image('animation_sheet.png')

        self.machine = Machine(
            model=self,
            states=['IDLE', 'SLEEP', 'RUN'],
            initial='IDLE',
            transitions=[
                {
                    'trigger': 'fall_asleep',
                    'source': 'IDLE',
                    'dest': 'SLEEP'
                },
                {
                    'trigger': 'wake_up',
                    'source': 'SLEEP',
                    'dest': 'IDLE'
                },
                                {
                    'trigger': 'start_run',
                    'source': ['IDLE', 'SLEEP'],
                    'dest': 'RUN'
                },
                {
                    'trigger': 'stop_run',
                    'source': 'RUN',
                    'dest': 'IDLE'
                }
            ],
            auto_transitions=False
        )

        self.on_enter_IDLE()

    def on_enter_IDLE(self):
        self.frame = 0
        self.idle_start_time = time.monotonic()

    def on_enter_SLEEP(self):
        self.frame = 0
        self.left_pressed = False
        self.right_pressed = False

    def on_enter_RUN(self):
        self.frame = 0

    def handle_event(self, event):
        # 자는 중 SPACE를 누르면 IDLE로 돌아간다.
        if self.state == 'SLEEP':
            if event.type == SDL_KEYDOWN and event.key == SDLK_SPACE:
                self.wake_up()
                return

        # 자는 중에도 방향키 입력을 처리한다.
        if event.type == SDL_KEYDOWN:
            if event.key == SDLK_LEFT:
                self.left_pressed = True
                self.face_dir = -1
            elif event.key == SDLK_RIGHT:
                self.right_pressed = True
                self.face_dir = 1
            else:
                return

        elif event.type == SDL_KEYUP:
            if event.key == SDLK_LEFT:
                self.left_pressed = False
            elif event.key == SDLK_RIGHT:
                self.right_pressed = False
            else:
                return
        else:
            return

        # IDLE과 SLEEP 모두 RUN으로 전환할 수 있다.
        if self.left_pressed or self.right_pressed:
            if self.state in ['IDLE', 'SLEEP']:
                self.start_run()
        else:
            if self.state == 'RUN':
                self.stop_run()

    def update(self):
        if self.state == 'IDLE':
            self.frame = (self.frame + 1) % 5

            if time.monotonic() - self.idle_start_time >= 5.0:
                self.fall_asleep()

        elif self.state == 'RUN':
            self.frame = (self.frame + 1) % 8

            direction = 0

            if self.left_pressed:
                direction -= 1
            if self.right_pressed:
                direction += 1

            self.x += direction * self.speed

            if direction > 0:
                self.face_dir = 1
            elif direction < 0:
                self.face_dir = -1

            # 이미지 폭이 100이므로 중심을 양끝에서 50만큼 제한
            self.x = max(
                50,
                min(get_canvas_width() - 50, self.x)
            )

    def draw(self):
        if self.state == 'RUN':
            # 달리기: 오른쪽 행 100, 왼쪽 행 0
            if self.face_dir == 1:
                row = 100
            else:
                row = 0

            self.image.clip_draw(
                self.frame * 100, row,
                100, 100,
                self.x, self.y
            )

        elif self.state == 'IDLE':
            if self.face_dir == 1:
                row = 300
            else:
                row = 200

            self.image.clip_draw(
                self.frame * 100, row,
                100, 100,
                self.x, self.y
            )

        elif self.state == 'SLEEP':
            if self.face_dir == 1:
                row = 300
            else:
                row = 200

            self.image.clip_composite_draw(
                0, row, 100, 100,
                3.141592 / 2, '',
                self.x, self.y - 25,
                100, 100
            )