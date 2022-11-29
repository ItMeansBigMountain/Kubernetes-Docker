import os

# GLOBAL INIT
files = os.listdir()
resource_components = {}

ordered_list = ["namespace" , "secret" , "config" , "depl" , "service"]
output_reference = { x:[] for x in ordered_list}




def _condition_then_append(resourceName, f):
    if resourceName not in resource_components:
        resource_components[resourceName] = 1
    else:
        resource_components[resourceName] += 1
    
    output_reference[resourceName].append(f)
    return resource_components




def sorting(f):
    if "namespace" in f:
        resource_components = _condition_then_append("namespace" , f)
    elif "secret" in f:
        resource_components = _condition_then_append("secret" , f)
    elif "config" in f:
        resource_components = _condition_then_append("config" , f)
    elif "depl" in f:
        resource_components = _condition_then_append("depl" , f)
    elif "service" in f:
        resource_components = _condition_then_append("service" , f)


def main():
    for f in files:
        sorting(f)

    print(ordered_list)    
    # print(output_reference)    
    # print(resource_components)    
    for key, value in output_reference.items():
        for f in value:
            o = os.system(f"kubectl apply -f {f}")






if __name__ == "__main__":
    main()