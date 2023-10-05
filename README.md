# �wPython�ł͂��߂�I�[�v���G���h�Ȑi���I�A���S���Y���x�T�|�[�g�y�[�W

<!-- 
```
brew install graphviz
conda create -n openevo python=3.8
conda activate openevo
conda install matplotlib==3.0.3
pip install -r requirements.txt
```

and install evogym.
https://evolutiongym.github.io/tutorials/getting-started.html
-->

## ���ƃC���X�g�[�����@

�I�[�v���G���h�ȃA���S���Y���������ς݂̃T���v���v���O������p�ӂ��܂����B����
�T���v���v���O�����ɂ́A�������̎�����p�ӂ��Ă��܂��B�����𓮍삳���Ȃ���A
�A���S���Y�����w��ł��������܂��B�����ł̓T���v���v���O�����ƁA���̎��s���̃C
���X�g�[�����@��������܂��B

### Python��Anaconda

�T���v���v���O������Python�Ŏ�������Ă��܂��B�܂��{���Ŏg�p���Ă���Evolution
Gym 1.0��Python 3.8���T�|�[�g���Ă��܂��B���̂��ߖ{���ł��APython 3.8���g�p����
���BPython 3.8�̃C���X�g�[�����@�ɂ��Ă͊������܂��B�܂�Anaconda���g�p���܂�
���AAnaconda�̃C���X�g�[�����@�ɂ��Ă͊������܂��B

 - Python�Fhttps://www.python.org/downloads/
 - Anaconda�Fhttps://docs.anaconda.com/

### Evolution Gym

�T���v���v���O�����ł�Evolution Gym���g���܂��BEvolution Gym�̓V�~�����[�V��
���̌��ʂ�\�����邽�߂�OpenGL���g�p���A�C���X�g�[�����ɃV�~�����[�^���r���h��
�܂��B�r���h�ɂ͒ǉ��̃��C�u�������K�v�ɂȂ�܂��B

#### Windows

Windows�ł͎��O��Git��Visual Studio���C���X�g�[������K�v������܂��B�ˑ���
�C�u�������C���X�g�[������ɂ� `winget` �R�}���h��p���܂��B

```
$ winget install cmake
```

���̌�A`conda` �R�}���h��Evolution Gym���C���X�g�[�����܂��B

```
$ git clone --recurse-submodules https://github.com/EvolutionGym/evogym.git
$ cd evogym
$ conda env create -f environment.yml
```

#### GNU/Linux�i��Ƃ���Ubuntu�j

GNU/Linux�̗�Ƃ���Ubuntu�ł̊��̍\�z���@��������܂��BUbuntu�ł�apt�R
�}���h��p���Ĉˑ����C�u�������C���X�g�[�����܂��B

```
$ apt install cmake glfw
```

���̌�A`conda` �R�}���h��Evolution Gym���C���X�g�[�����܂��B

```
$ git clone --recurse-submodules https://github.com/EvolutionGym/evogym.git
$ cd evogym
$ conda env create -f environment.yml
```

#### macOS

macOS�̗�Ƃ���Homebrew���g�������̍\�z���@��������܂��B

```
$ brew install cmake glfw
```

���̌�A `conda` �R�}���h��Evolution Gym���C���X�g�[�����܂��B
```
$ git clone --recurse-submodules https://github.com/EvolutionGym/evogym.git
$ cd evogym
$ conda env create -f environment.yml
```

|*����*�F<br>Evolution Gym�̃C���X�g�[���̍ہA�v���b�g�t�H�[���ɂ���Ă̓G���[���o�邱�Ƃ�����܂��B���̍ۂ́A�������URL�����g�����������B<br>https://github.com/oreilly-japan/evogym|
|:-|
