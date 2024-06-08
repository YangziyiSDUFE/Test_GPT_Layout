import unreal
import json


def load_from_js():
    with open("./layout.json") as f:
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
            f_path = '/Game/StarterContent/Props/SM_Chair.SM_Chair'

    elif name.startswith("coffee table"):
        f_path = '/Game/StarterContent/Props/SM_TableRound.SM_TableRound'
    elif name.startswith('sofa'):
        f_path = '/Game/StarterContent/Props/SM_Couch.SM_Couch'
    elif name.startswith('chandelier'):
        f_path = '/Game/Low_Poly_Viking_Interiors/Models/Props/Lights/SM_Chandelier_03.SM_Chandelier_03'
    elif name.startswith('plant'):
        f_path = '/Game/StarterContent/Props/SM_Statue.SM_Statue'
    else:
        f_path = "/Game/StarterContent/Shapes/Shape_WideCapsule"

    return f_path
    

if __name__ == "__main__":
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


