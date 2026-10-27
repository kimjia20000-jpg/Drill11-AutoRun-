from pico2d import (
    load_image, get_canvas_width,
    SDL_KEYDOWN, SDL_KEYUP,
    SDLK_LEFT, SDLK_RIGHT, SDLK_SPACE, SDLK_a
)
from transitions import Machine
import time


class AutoRun:
    def enter(self, boy):
        boy.frame = 0
        boy.left_pressed = False
        boy.right_pressed = False
    
    def update(self, boy):
        boy.frame = (boy.frame + 1) % 8

        # 일반 RUN의 2배 속도로 자동 이동
        boy.x += boy.face_dir * boy.speed * 2

        # 확대된 이미지 폭 150의 절반만큼 경계 확보
        left_edge = 75
        right_edge = get_canvas_width() - 75

        if boy.x >= right_edge:
            boy.x = right_edge
            boy.face_dir = -1

        elif boy.x <= left_edge:
            boy.x = left_edge
            boy.face_dir = 1

    def draw(self, boy):
        if boy.face_dir == 1:
            row = 100
        else:
            row = 0

        # 100×100에서 150×150으로 확대
        # 이미지 아래쪽 높이를 유지하도록 중심을 25 올림
        boy.image.clip_draw(
            boy.frame * 100, row,
            100, 100,
            boy.x, boy.y + 25,
            150, 150
        )


class Boy:
    def __init__(self):
        self.x, self.y = 400, 90
        self.frame = 0
        self.face_dir = 1
        self.speed = 5

        self.left_pressed = False
        self.right_pressed = False

        self.image = load_image('animation_sheet.png')
        self.auto_run = AutoRun()

        self.machine = Machine(
            model=self,
            states=['IDLE', 'SLEEP', 'RUN', 'AUTO_RUN'],
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
                },
                {
                    'trigger': 'start_auto_run',
                    'source': 'IDLE',
                    'dest': 'AUTO_RUN'
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

    def on_enter_AUTO_RUN(self):
        self.auto_run.enter(self)

    def handle_event(self, event):
        # IDLE에서 A키를 누르면 AutoRun으로 전환
        if self.state == 'IDLE':
            if event.type == SDL_KEYDOWN and event.key == SDLK_a:
                self.start_auto_run()
                return

        # AutoRun의 취소 입력은 이후 단계에서 추가
        if self.state == 'AUTO_RUN':
            return

        # 자는 중 SPACE를 누르면 IDLE로 전환
        if self.state == 'SLEEP':
            if event.type == SDL_KEYDOWN and event.key == SDLK_SPACE:
                self.wake_up()
                return

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

        if self.left_pressed or self.right_pressed:
            if self.state in ['IDLE', 'SLEEP']:
                self.start_run()
        else:
            if self.state == 'RUN':
                self.stop_run()

    def update(self):
        if self.state == 'AUTO_RUN':
            self.auto_run.update(self)

        elif self.state == 'IDLE':
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

            self.x = max(
                50,
                min(get_canvas_width() - 50, self.x)
            )

    def draw(self):
        if self.state == 'AUTO_RUN':
            self.auto_run.draw(self)

        elif self.state == 'RUN':
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