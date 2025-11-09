
# Render MugTree-mug_rand-v1


create and initialize the environment: `MugTree-mug_rand-v1`
```python
env = make(args.env_name)
env.reset()

prev_act = env.get_prev_action()
obs, *_ = env.step(prev_act)
```
```python
with table.figure_row() as row:
    for i, img_key in enumerate(args.image_keys.split(",")):
        img = obs[img_key]
        print("data type is", img.dtype)

        fname = f"{figures_dir}/{img_key}.png?ts={doc.now()}"
        row.figure(img, src=fname, title=img_key, caption="this is the details")
```

| **front/rgb** | **right/rgb** | **wrist/rgb** |
|:-------------:|:-------------:|:-------------:|
| ![figures/MugTree-mug_rand-v1/front/rgb.png?ts=2025-05-06 20:29:25.215548-04:00](figures/MugTree-mug_rand-v1/front/rgb.png?ts=2025-05-06 20:29:25.215548-04:00) | ![figures/MugTree-mug_rand-v1/right/rgb.png?ts=2025-05-06 20:29:25.245987-04:00](figures/MugTree-mug_rand-v1/right/rgb.png?ts=2025-05-06 20:29:25.245987-04:00) | ![figures/MugTree-mug_rand-v1/wrist/rgb.png?ts=2025-05-06 20:29:25.254667-04:00](figures/MugTree-mug_rand-v1/wrist/rgb.png?ts=2025-05-06 20:29:25.254667-04:00) |
| this is the details | this is the details | this is the details |

### Visualizing Random Placement

visualize random placement by aggregating top-down views:

```python
# Collect 10 images after resets
images = []
first_key = "top/rgb"

# stop the loop
while raw_env.task.pose_buffer:
    obs = env.reset()
    images.append(obs[first_key].astype(np.float32))

# Average the images
max_img = np.max(images, axis=0).astype(np.uint8)
min_img = np.min(images, axis=0).astype(np.uint8)
```
```python
with table.figure_row() as row:
    row.figure(max_img, src=fname_max, title=f"Max Mixed{first_key}", caption=caption)
    row.figure(min_img, src=fname_min, title=f"Min Mixed {first_key}", caption=caption)
```

| **Max Mixedtop/rgb** | **Min Mixed top/rgb** |
|:--------------------:|:---------------------:|
| ![figures/MugTree-mug_rand-v1/maxmix_top/rgb.png?ts=2025-05-06 20:29:26.271581-04:00](figures/MugTree-mug_rand-v1/maxmix_top/rgb.png?ts=2025-05-06 20:29:26.271581-04:00) | ![figures/MugTree-mug_rand-v1/minmix_top/rgb.png?ts=2025-05-06 20:29:26.271603-04:00](figures/MugTree-mug_rand-v1/minmix_top/rgb.png?ts=2025-05-06 20:29:26.271603-04:00) |
| top/rgb | top/rgb |
