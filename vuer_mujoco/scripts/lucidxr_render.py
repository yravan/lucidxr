import os

from cmx import CommonMark
from params_proto import ParamsProto
from tqdm import tqdm

from vuer_mujoco.tasks import make


class Args(ParamsProto, cli=False):
    env_name: str = "Mug_tree-v1"


def main():
    doc = CommonMark(Args.env_name + ".md", root=os.getcwd(), prefix=".")

    doc @ """
    # Render Mug Tree Task


    """

    names = {0: "top", 1: "front", 2: "right", 3: "right_r", 4: "wrist"}

    t = doc.table()
    with doc:
        import matplotlib.pyplot as plt

        env_name = "MugTree-fixed-v1"
        env = make(env_name)
        env.reset()

        for i in tqdm([0, 4, 1, 2, 3]):
            if i in [0, 2]:
                r = t.figure_row()

            img = env.render("rgb_array", camera_id=i)

            name = names[i]

            plt.title(name.capitalize(), fontsize=20)
            plt.imshow(img)
            plt.axis("off")

            plt.margins(0, 0)
            plt.subplots_adjust(top=1, bottom=0, right=1, left=0, hspace=0, wspace=0)
            plt.tight_layout()

            r.savefig(f"{Args.env_name}/camera_{i:02d}_rgb.png", title=name)

    doc.flush()


if __name__ == "__main__":
    main()
