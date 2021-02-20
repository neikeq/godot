def get_name() -> str:
    return 'mono'

def can_build(env: dict) -> bool:
    supported_platforms = ["windows", "osx", "linuxbsd",
                           "server", "android", "haiku", "javascript", "iphone"]
    return env.platform in supported_platforms


def get_doc_classes() -> [str]:
    return [
        "CSharpScript",
        "GodotSharp",
    ]


def get_doc_path() -> str:
    return "doc_classes"
