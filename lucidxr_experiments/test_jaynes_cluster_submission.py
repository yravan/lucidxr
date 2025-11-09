import jaynes

def train():
    print('hello world')

jaynes.config(mode="train", verbose=True, config_path="./.jaynes_fortyfive.yml")
jaynes.run(train)
jaynes.listen()
