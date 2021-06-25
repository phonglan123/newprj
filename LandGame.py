import sys
import os
import hashlib
if sys.version_info < (3, 6):
    import sha3
from datetime import datetime
from ast import literal_eval

def hash_string(string):
    return hashlib.new('sha3_512', string.encode()).hexdigest()

class Block_in_chain:
    def __init__(self, blocks_list, signature = 'P'):
        self.signature = signature
        self.blocks_list = blocks_list
        self.root_content = 'NAM QUỐC SƠN HÀ NAM ĐẾ CƯ!'

    def __hash_block(self, previous_block_hash, block_content):
        return hash_string(previous_block_hash + self.signature + block_content)

    def check_block(self, block_id):
        if block_id == 0:
            return self.blocks_list[0][2] == self.__hash_block('0' * 128, self.root_content)
        
        block = self.blocks_list[block_id]
        previous_block = self.blocks_list[block_id-1]
        
        block_check = (block[2] == self.__hash_block(block[0], block[1]))
        previous_block_check_first = (previous_block[2] == self.__hash_block(previous_block[0], previous_block[1]))
        previous_block_check_second = (block[0] == self.__hash_block(previous_block[0], previous_block[1]))

        return (block_check and previous_block_check_first and previous_block_check_second)

    def add_block(self, block_content):
        if len(self.blocks_list) == 0:
            root_block_hash = self.__hash_block('0' * 128, self.root_content)
            self.blocks_list.append(['0' * 128, self.root_content, root_block_hash])
        if self.check_block(len(self.blocks_list) - 1):
            lastest_block = self.blocks_list[-1]
            block_hash = self.__hash_block(lastest_block[2], block_content)
            self.blocks_list.append([lastest_block[2], block_content, block_hash])
        return {
            'new_block_id': len(self.blocks_list) - 1,
            'new_block_content': self.blocks_list[-1]
        }

class Map:
    def __init__(self, map_list, map_name):
        self.map = map_list
        self.map_name = map_name

    def change_land_info(self, info):
        certificate = str(datetime.now()) + '|land|' + str(info)
        block = Block_in_chain(log, self.map_name).add_block(certificate)
        new_hash = hash_string(str(block['new_block_id']) + str(block['new_block_content']))
        self.map[info['y']][info['x']] = str(block['new_block_id']) + '-' + new_hash

    def get_land_info(self, coord_x, coord_y):
        data = self.map[coord_y][coord_x].split('-')
        block_id = int(data[0])
        block_content = log[block_id]
        temp_hash = hash_string(str(block_id) + str(log[block_id]))

        first_check = Block_in_chain(log, self.map_name).check_block(block_id)
        second_check = (data[1] == temp_hash)
        
        if (first_check and second_check):
            certificate = block_content[1].split('|')
            return literal_eval(certificate[2])

class Player:
    def __init__(self, player_list, map_name):
        self.player_list = player_list
        self.map_name = map_name
        
    def change_player_info(self, username, info):
        certificate = str(datetime.now()) + '|player|' + str(info)
        block = Block_in_chain(log, self.map_name).add_block(certificate)
        new_hash = hash_string(str(block['new_block_id']) + str(block['new_block_content']))
        self.player_list[username] = str(block['new_block_id']) + '-' + new_hash

    def get_player_info(self, username):
        data = self.player_list[username].split('-')
        block_id = int(data[0])
        block_content = log[block_id]
        temp_hash = hash_string(str(block_id) + str(log[block_id]))

        first_check = Block_in_chain(log, self.map_name).check_block(block_id)
        second_check = (data[1] == temp_hash)
        
        if (first_check and second_check):
            certificate = block_content[1].split('|')
            return literal_eval(certificate[2])

class GameCtrl:
    def player_sign_up(self, username, password):
        Player(player_list, map_name).change_player_info(username, {
            'password': hash_string(password),
            'info': {
                'display_name': username,
                'intro': username,
            },
            'lands': []
        })
        return '[P/success]'

    def player_sign_in(self, username, password):
        if username not in player_list.keys():
            return '[P/error]WRONG_USERNAME'
        elif hash_string(password) == Player(player_list, map_name).get_player_info(username)['password']:
            return '[P/success]'
        else:
            return '[P/error]WRONG_PASSWORD'

    def player_change_info(self, username, info_name, new_value):
        player_info = Player(player_list, map_name).get_player_info(username)
        player_info['info'][info_name] = new_value
        Player(player_list, map_name).change_player_info(username, player_info)

    def player_change_password(self, username, new_password):
        player_info = Player(player_list, map_name).get_player_info(username)
        player_info['password'] = hash_string(new_password)
        Player(player_list, map_name).change_player_info(username, player_info)

    def land_buy_new(self, username, coord_x, coord_y, land_name):
        Map(map_list, map_name).change_land_info({
            'x': coord_x,
            'y': coord_y,
            'owner_username': username,
            'land_name': land_name,
            'item': item_list[0]
        })
        player_info = Player(player_list, map_name).get_player_info(username)
        player_info['lands'].append([coord_x, coord_y])
        Player(player_list, map_name).change_player_info(username, player_info)

    def land_change_info(self, username, coord_x, coord_y, info_name, new_value):
        if info_name == 'owner_username':
            if new_value not in player_list.keys():
                return '[P/error]WRONG_USERNAME'
            else:
                player_info = Player(player_list, map_name).get_player_info(username)
                player_info['lands'].remove([coord_x, coord_y])
                Player(player_list, map_name).change_player_info(username, player_info)
        
        land_info = Map(map_list, map_name).get_land_info(coord_x, coord_y)
        land_info[info_name] = new_value
        Map(map_list, map_name).change_land_info(land_info)

class PlayerCtrl:
    def __init__(self, username, password):
        if username not in player_list.keys():
            GameCtrl().player_sign_up(username, password)
        self.username = username
        self.password = password
        
    def start(self):
        return GameCtrl().player_sign_in(self.username, self.password)

    def sign_out(self):
        self.username = ''
        self.password = ''

    def change_password(self, old_password, new_password):
        if GameCtrl().player_sign_in(self.username, old_password) == '[P/success]':
            GameCtrl().player_change_password(self.username, new_password)
            self.password = new_password
            return '[P/success]'
        else:
            return GameCtrl().player_sign_in(self.username, old_password)

    def buy_new_land(self, coord_x, coord_y):
        GameCtrl().land_buy_new(self.username, (coord_x - 1), (coord_y - 1), self.username)

    def change_info(self, info_name, options):
        if GameCtrl().player_sign_in(self.username, self.password) == '[P/success]':
            if info_name == 'player_display_name':
                GameCtrl().player_change_info(self.username, 'display_name', options)
            elif info_name == 'player_intro':
                GameCtrl().player_change_info(self.username, 'intro', options)
            elif info_name == 'land_owner':  
                GameCtrl().land_change_info(self.username, (options[0] - 1), (options[1] - 1), 'owner_username', options[2])
            elif info_name == 'land_item':
                GameCtrl().land_change_info(self.username, (options[0] - 1), (options[1] - 1), 'item', options[2])
            elif info_name == 'land_name':
                GameCtrl().land_change_info(self.username, (options[0] - 1), (options[1] - 1), 'land_name', options[2])
        else:
            return '[P/error]CAN_NOT_AUTHENTICATE'

    def get_info(self, info_name, land_coord = None):
        old_info_name = ['display_name', 'intro', 'owner_username', 'item', 'land_name']
        new_info_name = ['player_display_name', 'player_intro', 'land_owner', 'land_item', 'land_name']
        info_name = old_info_name[new_info_name.index(info_name)]
        if land_coord == None:
            player_info = Player(player_list, map_name).get_player_info(self.username)
            return player_info['info'][info_name]
        else:
            land_info = Map(map_list, map_name).get_land_info(land_coord[0] - 1, land_coord[1] - 1)
            return land_info[info_name]

class ConsoleCtrl:
    def __init__(self):
        self.player = None

    def start(self):
        os.system('cls')
        print('---- Đăng nhập / Đăng kí ----')
        username = input('Tên đăng nhập: ')
        password = input('Mật khẩu: ')
        self.player = PlayerCtrl(username, password)
        self.username = username
        login_alert = self.player.start()
        if login_alert == '[P/success]':
            self.menu()
        elif login_alert == '[P/error]WRONG_USERNAME':
            print('=> Sai tên đăng nhập, bấm Enter để quay lại...')
            input()
            ConsoleCtrl().start()
        elif login_alert == '[P/error]WRONG_PASSWORD':
            print('=> Sai mật khẩu, bấm Enter để quay lại...')
            input()
            ConsoleCtrl().start()

    def menu(self):
        os.system('cls')
        print('Chào mừng trở lại, ' + self.player.get_info('player_display_name'))
        print('# ' + self.player.get_info('player_intro') + ' #')
        print()
        print('Dưới đây là menu chương trình, hãy đưa ra sự lựa chọn của bạn:')
        print('1. Đổi mật khẩu')
        print('2. Đổi tên hiển thị')
        print('3. Đổi đoạn giới thiệu cá nhân')
        print('4. Xem bản đồ')
        print('5. Đăng xuất')
        print('6. Thoát chương trình')
        print()
        self.menu_choose(int(input('Nhập sự lựa chọn (số thứ tự): ')))

    def menu_choose(self, number):
        if number == 1:
            os.system('cls')
            old_password = input('Nhập mật khẩu hiện tại: ')
            new_password = input('Nhập mật khẩu mới: ')
            login_alert = self.player.change_password(old_password, new_password)
            if login_alert == '[P/success]':
                print('=> Thay đổi mật khẩu thành công, bấm Enter để quay lại...')
                input()
                self.menu()
            elif login_alert == '[P/error]WRONG_USERNAME':
                print('=> Sai tên đăng nhập, bấm Enter để quay lại...')
                input()
                self.menu()
            elif login_alert == '[P/error]WRONG_PASSWORD':
                print('=> Sai mật khẩu, bấm Enter để quay lại...')
                input()
                self.menu()
        elif number == 2:
            os.system('cls')
            self.player.change_info('player_display_name', input('Nhập tên hiển thị mới: '))
            print('=> Thay đổi tên hiển thị thành công, bấm Enter để quay lại...')
            input()
            self.menu()
        elif number == 3:
            os.system('cls')
            self.player.change_info('player_intro', input('Nhập đoạn giới thiệu bản thân mới: '))
            print('=> Thay đổi đoạn giới thiệu bản thân thành công, bấm Enter để quay lại...')
            input()
            self.menu()
        elif number == 4:
            self.map_menu()
        elif number == 5:
            self.player.sign_out()
            ConsoleCtrl().start()
        elif number == 6:
            os.system('cls')

    def map_menu(self):
        os.system('cls')
        self.get_map()
        print()
        print('---- Menu ----')
        print('Dưới đây là menu của Bản đồ, hãy đưa ra sự lựa chọn của bạn:')
        print('1. Xem ô đất')
        print('2. Chỉnh sửa ô đất (nếu bạn là chủ)')
        print('3. Quay lại menu chính')
        print()
        self.map_menu_choose(int(input('Nhập sự lựa chọn (số thứ tự): ')))

    def get_map(self):
        print('---- Bản đồ ----')
        col_amount = len(map_list[0])
        col_index_num = [str(col_index) for col_index in range(2, col_amount + 1)]
        col_index_str = '  '.join(col_index_num)
        print('     1  ' + col_index_str)
        for index, row in enumerate(map_list):
             print('  ' + str(index + 1) + '  ' + self.map_row_format(row, index))

    def map_row_format(self, row, coord_y):
        row_str = []
        for coord_x, col in enumerate(row):
            if col == None:
                row_str.append('□')
            else:
                land_item = self.player.get_info('land_item', [coord_x + 1, coord_y + 1])
                row_str.append(land_item[0])
        return '  '.join(row_str)

    def map_menu_choose(self, number):
        if number == 1:
            os.system('cls')
            self.get_map()
            print()
            print('---- Xem ô đất ----')
            coord_x = int(input('Nhập số thứ tự cột của ô muốn xem (chiều dọc): '))
            coord_y = int(input('Nhập số thứ tự hàng của ô muốn xem (chiều ngang): '))
            if map_list[coord_y - 1][coord_x - 1] == None:
                print('\nĐây là một ô đất trống, bạn có muốn mua nó?')
                buy_land_choice = input('Nhập sự lựa chọn (có ghi "c", không ghi "k"): ')
                if buy_land_choice == 'c':
                    self.player.buy_new_land(coord_x, coord_y)
                    print('=> Mua thành công, bấm Enter để quay lại...')
                    input()
                    self.map_menu()
                elif buy_land_choice == 'k':
                    self.map_menu()
            else:
                self.map_menu_show_land(coord_x, coord_y)
        elif number == 2:
            os.system('cls')
            self.get_map()
            print()
            print('---- Sửa ô đất ----')
            coord_x = int(input('Nhập số thứ tự cột của ô muốn sửa (chiều dọc): '))
            coord_y = int(input('Nhập số thứ tự hàng của ô muốn sửa (chiều ngang): '))
            if map_list[coord_y - 1][coord_x - 1] == None:
                print('=> Đây là một ô đất trống (bạn có thể chọn "1. Xem ô đất" để mua nó), bấm Enter để quay lại...')
                input()
                self.map_menu()
            elif self.username == self.player.get_info('land_owner', [coord_x, coord_y]):
                self.map_menu_change_land(coord_x, coord_y)
            else:
                print('=> Ô đất này không phải của bạn nên bạn không có quyền thay đổi, bấm Enter để quay lại...')
                input()
                self.map_menu()
        elif number == 3:
            self.menu()

    def map_menu_show_land(self, coord_x, coord_y):
        land_item = self.player.get_info('land_item', [coord_x, coord_y])
        land_owner = self.player.get_info('land_owner', [coord_x, coord_y])
        land_name = self.player.get_info('land_name', [coord_x, coord_y])
        os.system('cls')
        print('---- Xem ô đất ----')
        print('╔═══╗  Tên ô đất: ' + land_name)
        print('║ ' + land_item[0] + ' ║  Chủ sở hữu: ' + land_owner)
        print('╚═══╝  Vật phẩm: ' + land_item[1])
        print('Bạn đang xem ô đất x(' + str(coord_x) + ')y(' + str(coord_y) + '), bấm Enter để quay lại...')
        input()
        self.map_menu()

    def map_menu_change_land(self, coord_x, coord_y):
        land_item = self.player.get_info('land_item', [coord_x, coord_y])
        land_owner = self.player.get_info('land_owner', [coord_x, coord_y])
        land_name = self.player.get_info('land_name', [coord_x, coord_y])
        os.system('cls')
        print('---- Sửa ô đất ô đất ----')
        print('[Toạ độ] x(' + str(coord_x) + ')y(' + str(coord_y) + ')')
        print('╔═══╗  Tên ô đất: ' + land_name)
        print('║ ' + land_item[0] + ' ║  Chủ sở hữu: ' + land_owner)
        print('╚═══╝  Vật phẩm: ' + land_item[1])
        print('\nHãy đưa ra sự lựa chọn của bạn:')
        print('1. Đổi tên ô đất')
        print('2. Đổi chủ ô đất')
        print('3. Đặt vật phẩm')
        print('4. Quay lại menu chính')
        print('5. Xoá ô đất (trả về cho hệ thống)')
        print()
        self.map_menu_change_land_choose(int(input('Nhập sự lựa chọn (số thứ tự): ')), coord_x, coord_y)

    def map_menu_change_land_choose(self, number, coord_x, coord_y):
        if number == 1:
            self.player.change_info('land_name', [coord_x, coord_y, input('\nNhập tên mới cho ô đất: ')])
            print('=> Đổi tên thành công, bấm Enter để quay lại...')
            input()
            self.map_menu()
        elif number == 2:
            new_owner = input('\nNhập tên đăng nhập của chủ mới cho ô đất: ')
            if new_owner not in player_list.keys():
                print('=> Không tìm thấy người chơi với tên đăng nhập trên, bấm Enter để quay lại...')
                input()
                self.map_menu()
            else:
                self.player.change_info('land_owner', [coord_x, coord_y, new_owner])
                print('=> Đổi chủ thành công, bấm Enter để quay lại...')
                input()
                self.map_menu()
        elif number == 3:
            os.system('cls')
            print('---- Danh sách vật phẩm ----')
            for index, item in enumerate(item_list):
                print(str(index) + '. ' + item[1])
            print('\n---- Đổi vật phẩm ----')
            item_index = int(input('\nNhập số thứ tự vật phẩm cho ô đất: '))
            self.player.change_info('land_item', [coord_x, coord_y, item_list[item_index]])
            print('=> Đổi vật phẩm thành công, bấm Enter để quay lại...')
            input()
            self.map_menu()
        elif number == 4:
            self.map_menu()
        elif number == 5:
            map_list[coord_y - 1][coord_x - 1] = None
            print('\n=> Xoá ô đất thành công, bấm Enter để quay lại...')
            input()
            self.map_menu()

log = []
map_name = 'Việt Nam'
map_list = [[None] * 4 for col in range(6)]
player_list = {}
item_list = [
    ['■', 'Đất trống'],
    ['Q', 'Cái quạt'],
    ['Đ', 'Cái đèn']
]
ConsoleCtrl().start()

print('In next version: Save data to files, money system (pay to buy new land, put new item)')
