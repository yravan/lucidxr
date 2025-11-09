
# Render ObjPermanence-fixed-v1


create and initialize the environment: `ObjPermanence-fixed-v1`
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
| ![figures/ObjPermanence-fixed-v1/front/rgb.png?ts=2025-05-05 23:48:12.440159-04:00](figures/ObjPermanence-fixed-v1/front/rgb.png?ts=2025-05-05 23:48:12.440159-04:00) | ![figures/ObjPermanence-fixed-v1/right/rgb.png?ts=2025-05-05 23:48:12.465954-04:00](figures/ObjPermanence-fixed-v1/right/rgb.png?ts=2025-05-05 23:48:12.465954-04:00) | ![figures/ObjPermanence-fixed-v1/wrist/rgb.png?ts=2025-05-05 23:48:12.473674-04:00](figures/ObjPermanence-fixed-v1/wrist/rgb.png?ts=2025-05-05 23:48:12.473674-04:00) |
| this is the details | this is the details | this is the details |
