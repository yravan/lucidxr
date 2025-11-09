from asyncio import sleep

if __name__ == "__main__":
    from vuer import Vuer, VuerSession
    from vuer.schemas import MuJoCo

    vuer = Vuer()

    with open("../../assets/scene0001/scene_files.txt", "r") as f:
        file_list = [l.strip() for l in f.readlines()]

    print("loading", file_list.__len__(), "files")

    @vuer.spawn(start=True)
    async def main(proxy: VuerSession):
        proxy.add @ MuJoCo(
            key="default-sim",
            src="https://vuer-hub-production.s3.amazonaws.com/robocasa-scenes/scene0001/scene.mjcf.xml",
            assets=file_list,
        )
        while True:
            await sleep(10)


