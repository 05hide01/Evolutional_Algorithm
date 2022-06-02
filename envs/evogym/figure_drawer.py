import os
import pickle
import numpy as np

import matplotlib.pyplot as plt
from PIL import Image
import imageio
from pygifsicle import gifsicle

from gym_utils import make_vec_envs

from stable_baselines3 import PPO


RenderPaddings = {
    'Walker-v0'         : ((4, 4), (1, 8)),
    'BridgeWalker-v0'   : ((4, 4), (1, 8)),
    'CaveCrawler-v0'    : ((4, 4), (1, 8)),
    'Jumper-v0'         : ((2, 2), (1, 16)),
    'Flipper-v0'        : ((4, 4), (1, 10)),
    'Balancer-v0'       : ((4, 4), (1, 8)),
    'Balancer-v1'       : ((4, 4), (1, 8)),
    'UpStepper-v0'      : ((4, 4), (1, 10)),
    'DownStepper-v0'    : ((4, 4), (1, 8)),
    'ObstacleTraverser-v0'  : ((4, 4), (1, 10)),
    'ObstacleTraverser-v1'  : ((4, 4), (1, 10)),
    'Hurdler-v0'        : ((4, 4), (1, 10)),
    'GapJumper-v0'      : ((4, 4), (1, 10)),
    'PlatformJumper-v0' : ((4, 4), (1, 10)),
    'Traverser-v0'      : ((4, 4), (1, 10)),
    'Lifter-v0'         : ((2, 2), (1, 8)),
    'Carrier-v0'        : ((4, 4), (1, 8)),
    'Carrier-v1'        : ((4, 4), (1, 8)),
    'Pusher-v0'         : ((4, 4), (1, 8)),
    'Pusher-v1'         : ((4, 4), (1, 8)),
    'BeamToppler-v0'    : ((2, 2), (1, 8)),
    'BeamSlider-v0'     : ((2, 2), (1, 8)),
    'Thrower-v0'        : ((4, 4), (1, 12)),
    'Catcher-v0'        : ((2, 2), (1, 6)),
    'AreaMaximizer-v0'  : ((2, 2), (1, 8)),
    'AreaMinimizer-v0'  : ((2, 2), (1, 8)),
    'WingspanMazimizer-v0'  : ((2, 2), (1, 8)),
    'HeightMaximizer-v0'    : ((2, 2), (1, 8)),
    'Climber-v0'        : ((2, 2), (1, 2)),
    'Climber-v1'        : ((2, 2), (1, 2)),
    'Climber-v2'        : ((2, 2), (1, 2)),
    'BidirectionalWalker-v0': ((4, 4), (1, 8)),
}


def pool_init_func(lock_):
    global lock
    lock = lock_


def make_gif(filename, env, viewer, controller, controller_type, resolution=(256,144), deterministic=True):
    assert controller_type in ['NEAT', 'PPO']

    viewer.set_resolution(resolution)

    done = False
    obs = env.reset()
    imgs = []
    while not done:

        img = viewer.render(mode='img')
        imgs.append(img)

        if controller_type=='NEAT':
            action = [np.array(controller.activate(obs[0]))*2 - 1]
        elif controller_type=='PPO':
            action, _ = controller.predict(obs, deterministic=deterministic)
        else:
            return
        obs, _, done, infos = env.step(action)


    imageio.mimsave(filename, imgs, duration=(1/50.0))

    with lock:
        gifsicle(sources=filename,
                 destination=filename,
                 optimize=False,
                 colors=64,
                 options=["--optimize=3","--no-warnings"])

    return


def make_jpg(filename, env, viewer, controller, controller_type, padding, interval='timestep', resolution_scale=30, timestep_interval=40, distance_interval=0.8, display_timestep=True, deterministic=True):
    assert controller_type in ['NEAT', 'PPO']
    assert interval in ['timestep', 'distance', 'hybrid']

    grid_size = env.get_attr("world", indices=None)[0].grid_size

    view_size = (grid_size[0]+padding[0][0]+padding[0][1], grid_size[1]+padding[1][0]+padding[1][1])
    resolution = (view_size[0]*resolution_scale, view_size[1]*resolution_scale)
    camera_position = ((grid_size[0]-padding[0][0]+padding[0][1])/2, (grid_size[1]-padding[1][0]+padding[1][1])/2)

    viewer.track_objects()
    viewer.set_view_size(view_size)
    viewer.set_resolution(resolution)
    viewer.set_pos(camera_position)

    obs = env.reset()

    images = []
    alphas = []
    position_history = {}
    prev_position = None
    done = False
    while not done:

        position = env.env_method('get_pos_com_obs', object_name='robot')[0]
        time = env.env_method('get_time')[0]
        draw = False
        hide_voxels = False
        draw_main = True
        if interval=='timestep':
            if time%timestep_interval==0:
                draw = True
                mix_value = len(images)
        elif interval=='distance':
            if time==0 or np.linalg.norm(position-prev_position)>distance_interval:
                draw = True
                mix_value = len(position_history)
        elif interval=='hybrid':
            if time==0 or np.linalg.norm(position-prev_position)>distance_interval:
                draw = True
                mix_value = len(position_history)
            elif time%timestep_interval==0:
                draw = True
                mix_value = -2
                hide_voxels = True
                draw_main = False

        if draw:
            image = viewer.render(mode='img', hide_grid=True, hide_voxels=hide_voxels)
            alpha = np.where(np.mean(image, axis=-1)>240, 1e-3, 2**mix_value)

            images.append(image)
            alphas.append(np.expand_dims(alpha, axis=-1))

            if draw_main:
                position_history[time] = position
                prev_position = position

        if controller_type=='NEAT':
            action = [np.array(controller.activate(obs[0]))*2 - 1]
        elif controller_type=='PPO':
            action, _ = controller.predict(obs, deterministic=deterministic)
        else:
            return
        obs, _, done, infos = env.step(action)

    image = sum([image*alpha for image,alpha in zip(images, alphas)]) / sum(alphas)
    image = image.astype('uint8')

    fig, ax = plt.subplots(figsize=(view_size[0]/3, view_size[1]/3), dpi=4*resolution_scale)
    ax.imshow(image)

    if display_timestep:
        for time,position in position_history.items():
            x = (padding[0][0] + position[0]*10) * resolution_scale
            y = (padding[1][1] + grid_size[1] - position[1]*10 - 3.2) * resolution_scale
            ax.text(x,y,f't={time}', ha='center', fontsize=12)

    ax.axis('off')
    plt.savefig(filename, bbox_inches='tight')
    plt.close()

    return


class EvogymControllerDrawerNEAT():
    def __init__(self, save_path, env_id, structure, genome_config, decode_function, overwrite=True, save_type='gif', **draw_kwargs):
        assert save_type in ['gif', 'jpg']

        self.save_path = os.path.join(save_path, save_type)
        self.env_id = env_id
        self.structure = structure
        self.genome_config = genome_config
        self.decode_function = decode_function
        self.overwrite = overwrite
        self.save_type = save_type
        self.draw_kwargs = draw_kwargs

        os.makedirs(self.save_path, exist_ok=True)

    def draw(self, key, genome_file, directory=''):
        save_dir = os.path.join(self.save_path, directory)
        os.makedirs(save_dir, exist_ok=True)

        filename = os.path.join(save_dir, f'{key}.{self.save_type}')
        if not self.overwrite and os.path.exists(filename):
            return

        env = make_vec_envs(self.env_id, self.structure, 0, 1, allow_early_resets=False)
        viewer = env.get_attr("default_viewer", indices=None)[0]

        with open(genome_file, 'rb') as f:
            genome = pickle.load(f)
        controller = self.decode_function(genome, self.genome_config)

        if self.save_type=='gif':
            make_gif(filename, env, viewer, controller, 'NEAT', **self.draw_kwargs)

        elif self.save_type=='jpg':
            padding = RenderPaddings[self.env_id]
            make_jpg(filename, env, viewer, controller, 'NEAT', padding, **self.draw_kwargs)

        env.close()
        print(f'genome {key} ... done')
        return


class EvogymControllerDrawerPPO():
    def __init__(self, save_path, env_id, structure, overwrite=True, save_type='gif', **draw_kwargs):
        assert save_type in ['gif', 'jpg']

        self.save_path = os.path.join(save_path, save_type)
        self.env_id = env_id
        self.structure = structure
        self.overwrite = overwrite
        self.save_type = save_type
        self.draw_kwargs = draw_kwargs

        os.makedirs(self.save_path, exist_ok=True)

    def draw(self, iter, ppo_file, directory=''):
        save_dir = os.path.join(self.save_path, directory)
        os.makedirs(save_dir, exist_ok=True)

        filename = os.path.join(save_dir, f'{iter}.{self.save_type}')
        if not self.overwrite and os.path.exists(filename):
            return

        env = make_vec_envs(self.env_id, self.structure, 0, 1, allow_early_resets=False, vecnormalize=True)
        viewer = env.get_attr("default_viewer", indices=None)[0]

        controller = PPO.load(ppo_file)
        env.obs_rms = controller.env.obs_rms

        if self.save_type=='gif':
            make_gif(filename, env, viewer, controller, 'PPO', **self.draw_kwargs)

        elif self.save_type=='jpg':
            padding = RenderPaddings[self.env_id]
            make_jpg(filename, env, viewer, controller, 'PPO', padding, **self.draw_kwargs)

        env.close()
        print(f'iter {iter} ... done')
        return


class EvogymStructureDrawerCPPN():
    def __init__(self, save_path, env_id, overwrite=True, save_type='gif', **draw_kwargs):
        assert save_type in ['gif', 'jpg']

        self.save_path = os.path.join(save_path, save_type)
        self.env_id = env_id
        self.overwrite = overwrite
        self.save_type = save_type
        self.draw_kwargs = draw_kwargs

        os.makedirs(self.save_path, exist_ok=True)

    def draw(self, key, structure_file, ppo_file, directory=''):
        save_dir = os.path.join(self.save_path, directory)
        os.makedirs(save_dir, exist_ok=True)

        filename = os.path.join(save_dir, f'{key}.{self.save_type}')
        if not self.overwrite and os.path.exists(filename):
            return

        structure_data = np.load(structure_file)
        structure = (structure_data['robot'], structure_data['connectivity'])

        env = make_vec_envs(self.env_id, structure, 0, 1, allow_early_resets=False, vecnormalize=True)
        viewer = env.get_attr("default_viewer", indices=None)[0]

        controller = PPO.load(ppo_file)
        env.obs_rms = controller.env.obs_rms

        if self.save_type=='gif':
            make_gif(filename, env, viewer, controller, 'PPO', **self.draw_kwargs)

        elif self.save_type=='jpg':
            padding = RenderPaddings[self.env_id]
            make_jpg(filename, env, viewer, controller, 'PPO', padding, **self.draw_kwargs)

        env.close()
        print(f'genome {key} ... done')
        return




def save_controller_gif(env_id, structure, genome_key, genome_file, genome_config, decode_function, gif_file, resolution):

    with open(genome_file, 'rb') as f:
        genome = pickle.load(f)


    env = make_vec_envs(env_id, structure, 0, 1, allow_early_resets=False)
    env.get_attr("default_viewer", indices=None)[0].set_resolution(resolution)

    controller = decode_function(genome, genome_config)

    done = False
    obs = env.reset()
    img = env.render(mode='img')
    imgs = [img]
    while not done:
        action = np.array(controller.activate(obs[0]))*2 - 1
        obs, _, done, infos = env.step([action])
        img = env.render(mode='img')
        imgs.append(img)

    env.close()

    imageio.mimsave(gif_file, imgs, duration=(1/50.0))

    with lock:
        gifsicle(sources=gif_file,
                 destination=gif_file,
                 optimize=False,
                 colors=64,
                 options=["--optimize=3","--no-warnings"])

    print(f'genome {genome_key} ... done')
    return


def save_controller_ppo_gif(env_id, structure, iter, ppo_file, gif_file, resolution, deterministic=False):

    controller = PPO.load(ppo_file)

    env = make_vec_envs(env_id, structure, 0, 1, allow_early_resets=False, vecnormalize=True)
    env.get_attr("default_viewer", indices=None)[0].set_resolution(resolution)
    env.obs_rms = controller.env.obs_rms

    done = False
    obs = env.reset()
    img = env.render(mode='img')
    imgs = [img]
    while not done:
        action, _ = controller.predict(obs, deterministic=deterministic)
        obs, _, done, infos = env.step(action)
        img = env.render(mode='img')
        imgs.append(img)

    env.close()

    imageio.mimsave(gif_file, imgs, duration=(1/50.0))

    with lock:
        gifsicle(sources=gif_file,
                 destination=gif_file,
                 optimize=False,
                 colors=64,
                 options=["--optimize=3","--no-warnings"])

    print(f'iter {iter} ... done')
    return


def save_structure_gif(env_id, genome_key, ppo_file, structure_file, gif_file, resolution, deterministic=False):

    controller = PPO.load(ppo_file)

    structure_data = np.load(structure_file)
    structure = (structure_data['robot'], structure_data['connectivity'])

    env = make_vec_envs(env_id, structure, 1000, 1, allow_early_resets=False, vecnormalize=True)
    env.get_attr("default_viewer", indices=None)[0].set_resolution(resolution)
    env.obs_rms = controller.env.obs_rms

    done = False
    obs = env.reset()
    img = env.render(mode='img')
    imgs = [img]
    while not done:
        action, _ = controller.predict(obs, deterministic=deterministic)
        obs, _, done, infos = env.step(action)
        img = env.render(mode='img')
        imgs.append(img)

    env.close()

    imageio.mimsave(gif_file, imgs, duration=(1/50.0))

    with lock:
        gifsicle(sources=gif_file,
                 destination=gif_file,
                 optimize=False,
                 colors=64,
                 options=["--optimize=3","--no-warnings"])

    print(f'robot {genome_key} ... done')
    return
