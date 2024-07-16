import unreal
import json

def getDesign():
    from openai import OpenAI
    client = OpenAI()
    gpt_model = "gpt-3.5-turbo"
    demand = """设计一个布景大小为20m*20m的咖啡馆场景，需要有四个桌子(table)，每个桌子配两个凳子(chair)，两个沙发(sofa)和一个吧台(bar)，还需要一些景观画(paint)
            """
    completion = client.chat.completions.create(model=gpt_model,
                                                messages=[{"role": "system", "content": '''\
                                                           假设你是一名使用UE5引擎进行关卡开发的游戏内环境设计师，\
                                                           在接下来的场景中，会给定一个场景主题和场景大小，\
                                                           要求列出环境内存在哪些物品，\
                                                           物品摆放的坐标和物品根据其使用环境的缩放系数以及根据其形态和功能决定的物体朝向，可以存在多个同名物体，但是它们的需要独立列出坐标\
                                                           输出到表格中，并整理成JSON格式。
                                                           对于每一个物品，它应当独立地列出name:str、position:UE坐标系下的空间坐标，1*3数组、scale:UE坐标系下的空间向量，1*3数组，分别对应x、y、z方向上的缩放、rotation:UE坐标下的向量，1*3数组，代表物品朝向的法向量方向 四项，形如：
                                                           items:[
                                                                {
                                                                "name": "Counter1",
                                                                "position": [2, 18, 0],
                                                                "scale": [1, 1, 1],
                                                                "rotation": [0, 0, 0]
                                                                },
                                                                {
                                                                "name": "Counter2",
                                                                "position": [2, 18, 0],
                                                                "scale": [1, 1, 1],
                                                                "rotation": [0, 0, 0]
                                                                },
                                                           ]     
                                                                                                                    \
                                                           '''},
                                                          {"role": "user", "content": demand}]
                                                )
    res, _, _, _ = completion.choices[0].message
    print(res)
    with open("./format_json.json", 'w') as write_f:
        write_f.write(res[1])


def load_from_js():
    with open("format_json.json") as f:
        content = f.read()
        layout_json = json.loads(content)
    layout_json = layout_json["items"]

    file_list = []
    for i in layout_json:
        # print(i)
        name,pos,scale,rot =[item[1] for item in i.items() ]
        # print(f"{name}:{pos},{scale},{rot}")
        file_list.append([name,pos,scale,rot])
    return file_list


def load_asset(asset_path):
    """
    Load an asset from the given path.
    """
    asset = unreal.EditorAssetLibrary.load_asset(asset_path)
    if not asset:
        unreal.log_error(f"Failed to load asset from path: {asset_path}")
    return asset


def build_loc(loc,rot,scale):
    pos_x, pos_y, pos_z = loc
    rot_x, rot_y, rot_z = rot
    sca_x, sca_y, sca_z = scale
    actor_location = unreal.Vector(pos_x * 50, pos_y * 50, pos_z * 50)
    actor_rotation = unreal.Rotator(rot_x, rot_y, rot_z)
    actor_scale = unreal.Vector(sca_x, sca_y, sca_z)

    return actor_location,actor_rotation,actor_scale


def spawn_actor_from_asset(asset,loc,rot,scale):
    """
    Spawn an actor from the given asset.
    """
    if not asset:
        unreal.log_error("Cannot spawn actor because the asset is invalid.")
        return None

    editor_subsystem = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
    world = editor_subsystem.get_editor_world()
    if not world:
        unreal.log_error("Failed to get the editor world.")
        return None

    actor = unreal.EditorLevelLibrary.spawn_actor_from_object(asset,loc,rot)
    if not actor:
        unreal.log_error("Failed to spawn actor from asset.")
    actor.set_actor_scale3d(scale)
    
    return actor


def search_or_generate(name):
    name = name.lower()
    if name.startswith('chair'):
        f_path = "/Game/StarterContent/Props/SM_Chair.SM_Chair"
    elif name.startswith("table"):
        f_path = '/Game/StarterContent/Props/SM_TableRound.SM_TableRound'
    elif name.startswith('sofa'):
        f_path = '/Game/StarterContent/Props/SM_Couch.SM_Couch'
    elif name.startswith('bar'):
        f_path = '/Game/FreeFurniturePack/Meshes/SM_Classic_table.SM_Classic_table'
    elif name.startswith('chandelier'):
        f_path = '/Game/StarterContent/Shapes/Shape_WideCapsule'
    elif name.startswith('paint'):
        f_path = '/Game/FreeFurniturePack/Meshes/SM_Picture.SM_Picture'
    elif name.startswith('decorative painting'):
        f_path = '/Game/StarterContent/Shapes/Shape_WideCapsule'
    elif name.startswith('customer'):
        pass
    else:
        f_path = "/Game/StarterContent/Shapes/Shape_WideCapsule"

    return f_path
    

if __name__ == "__main__":
    getDesign()
    files = load_from_js()
    for f in files:
        f_path = search_or_generate(name = f[0])
        asset = load_asset(f_path)
        actor_location,actor_rotation,actor_scale = build_loc(f[1],f[3],f[2])        
        spawned_actor = spawn_actor_from_asset(asset, actor_location, actor_rotation, actor_scale)

        if spawned_actor:
            unreal.log("Successfully spawned actor from asset.")
        else:
            unreal.log_error("Failed to spawn actor from asset.")


