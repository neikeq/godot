using System;
using System.Runtime.InteropServices;
using Godot.Bridge;

// ReSharper disable InconsistentNaming

namespace Godot.NativeInterop
{
    internal static class InteropUtils
    {
        internal static bool TryCreateManagedForScriptInstance(IntPtr unmanaged, IntPtr rawGCHandle,
            out GodotObject theAliveGodotObjectOrNull)
            => TryCreateManagedForScriptInstance(unmanaged, rawGCHandle, out _, out theAliveGodotObjectOrNull);

        private static bool TryCreateManagedForScriptInstance(IntPtr unmanaged, IntPtr rawGCHandle,
            out godot_bool hasCsScriptInstance, out GodotObject theAliveGodotObjectOrNull)
        {
            hasCsScriptInstance = godot_bool.True; // This method is only called if this is the case.

            NativeFuncs.godotsharp_internal_lock_managed_lifetime_mutex();
            try
            {
                // First, after locking, check if another thread was ahead of us.

                if (rawGCHandle == IntPtr.Zero)
                {
                    // Need to get it again in case another thread got ahead of us and allocated it.
                    rawGCHandle = NativeFuncs.godotsharp_internal_unmanaged_get_script_instance_managed(
                        unmanaged, out hasCsScriptInstance);
                }

                if (rawGCHandle != IntPtr.Zero)
                {
                    if ((GodotObject)((GCHandle)rawGCHandle).Target is { Disposed: false } aliveGodotObj)
                    {
                        theAliveGodotObjectOrNull = aliveGodotObj;
                        return true;
                    }
                }

                // This can happen if the script or script instance were somehow removed before the lock could be acquired.
                // That wouldn't really be a thread-safe operation, but that's none of our business.
                if (!hasCsScriptInstance.ToBool())
                {
                    theAliveGodotObjectOrNull = null;
                    return false;
                }

                // No one got ahead of us. Create it.

                rawGCHandle =
                    NativeFuncs.godotsharp_internal_unmanaged_script_instance_create_managed_locked(unmanaged);

                if (rawGCHandle != IntPtr.Zero)
                {
                    if ((GodotObject)((GCHandle)rawGCHandle).Target is { Disposed: false } aliveGodotObj)
                    {
                        theAliveGodotObjectOrNull = aliveGodotObj;
                        return true;
                    }
                }
            }
            finally
            {
                NativeFuncs.godotsharp_internal_unlock_managed_lifetime_mutex();
            }

            theAliveGodotObjectOrNull = null;
            return false;
        }

        public static GodotObject UnmanagedGetManaged(IntPtr unmanaged)
        {
            // The native pointer may be null.
            if (unmanaged == IntPtr.Zero)
                return null;

            // First try to get the tied managed object from a CSharpInstance script instance.

            IntPtr rawGCHandle = NativeFuncs.godotsharp_internal_unmanaged_get_script_instance_managed(
                unmanaged, out godot_bool hasCsScriptInstance);

            if (rawGCHandle != IntPtr.Zero)
            {
                if ((GodotObject)((GCHandle)rawGCHandle).Target is { Disposed: false } aliveGodotObj)
                    return aliveGodotObj;
            }

            // If the object has a CSharpInstance script instance,
            // then the script instance's managed object was collected or disposed (as per the previous check),
            // create a new managed object.

            if (hasCsScriptInstance.ToBool())
            {
                if (TryCreateManagedForScriptInstance(unmanaged, rawGCHandle, out hasCsScriptInstance,
                        out var godotObject))
                {
                    return godotObject;
                }

                // Might change. That wouldn't really be a thread-safe operation, but that's none of our business.
                if (hasCsScriptInstance.ToBool())
                    return null;
            }

            // If it doesn't have a CSharpInstance script instance,
            // try with native instance bindings.

            rawGCHandle = NativeFuncs.godotsharp_internal_unmanaged_get_instance_binding_managed(unmanaged);

            if (rawGCHandle != IntPtr.Zero)
            {
                if ((GodotObject)((GCHandle)rawGCHandle).Target is { Disposed: false } aliveGodotObj)
                    return aliveGodotObj;
            }

            // If the native instance binding's managed object was collected or disposed,
            // create a new one.

            if (TryCreateManagedForInstanceBinding(out GodotObject aliveGodotObject))
                return aliveGodotObject;

            return null;

            bool TryCreateManagedForInstanceBinding(out GodotObject theAliveGodotObjectOrNull)
            {
                // NOTE: rawGCHandle is the local variable from the outer method.

                NativeFuncs.godotsharp_internal_lock_managed_lifetime_mutex();
                try
                {
                    // First, after locking, check if another thread was ahead of us.

                    if (rawGCHandle == IntPtr.Zero)
                    {
                        // Need to get it again in case another thread got ahead of us and allocated it.
                        rawGCHandle =
                            NativeFuncs.godotsharp_internal_unmanaged_get_instance_binding_managed_locked(unmanaged);
                    }

                    if (rawGCHandle != IntPtr.Zero)
                    {
                        if ((GodotObject)((GCHandle)rawGCHandle).Target is { Disposed: false } aliveGodotObj)
                        {
                            theAliveGodotObjectOrNull = aliveGodotObj;
                            return true;
                        }
                    }

                    // No one got ahead of us. Create it.

                    rawGCHandle =
                        NativeFuncs.godotsharp_internal_unmanaged_instance_binding_create_managed_locked(unmanaged);

                    if (rawGCHandle != IntPtr.Zero)
                    {
                        if ((GodotObject)((GCHandle)rawGCHandle).Target is { Disposed: false } aliveGodotObj)
                        {
                            theAliveGodotObjectOrNull = aliveGodotObj;
                            return true;
                        }
                    }
                }
                finally
                {
                    NativeFuncs.godotsharp_internal_unlock_managed_lifetime_mutex();
                }

                theAliveGodotObjectOrNull = null;
                return false;
            }
        }

        public static void TieManagedToUnmanaged(GodotObject managed, IntPtr unmanaged,
            StringName nativeName, bool refCounted, Type type, Type nativeType)
        {
            GCHandle strongGCHandle;
            GCHandle weakGCHandle;

            if (refCounted)
            {
                // Strong reference disabled by default, the GCHandle will be allocated whenever needed.
                strongGCHandle = default;
                weakGCHandle = CustomGCHandle.AllocWeak(managed);
            }
            else
            {
                strongGCHandle = CustomGCHandle.AllocStrong(managed, type);
                // The weak GC handle is unused for non-RefCounted objects, and thus it's not allocated.
                weakGCHandle = default;
            }

            if (type == nativeType)
            {
                var nativeNameSelf = (godot_string_name)nativeName.NativeValue;
                NativeFuncs.godotsharp_internal_tie_native_managed_to_unmanaged(
                    GCHandle.ToIntPtr(strongGCHandle), GCHandle.ToIntPtr(weakGCHandle),
                    unmanaged, nativeNameSelf, refCounted.ToGodotBool());
            }
            else
            {
                unsafe
                {
                    // We don't dispose `script` ourselves here.
                    // `tie_user_managed_to_unmanaged` does it for us to avoid another P/Invoke call.
                    godot_ref script;
                    ScriptManagerBridge.GetOrLoadOrCreateScriptForType(type, &script);

                    // IMPORTANT: This must be called after GetOrCreateScriptBridgeForType
                    NativeFuncs.godotsharp_internal_tie_user_managed_to_unmanaged(
                        GCHandle.ToIntPtr(strongGCHandle), GCHandle.ToIntPtr(weakGCHandle),
                        unmanaged, &script, refCounted.ToGodotBool());
                }
            }
        }

        public static void TieManagedToUnmanagedWithPreSetup(GodotObject managed, IntPtr unmanaged,
            bool refCounted, Type type, Type nativeType)
        {
            if (type == nativeType)
                return;

            NativeFuncs.godotsharp_internal_object_get_existing_associated_gchandles(unmanaged,
                out IntPtr rawStrongGCHandle, out IntPtr rawWeakGCHandle);

            GCHandle strongGCHandle = CustomGCHandle.FromNullableIntPtr(rawStrongGCHandle);
            GCHandle weakGCHandle = CustomGCHandle.FromNullableIntPtr(rawWeakGCHandle);

            if (strongGCHandle.IsAllocated)
                strongGCHandle.Target = managed;
            else
                strongGCHandle = CustomGCHandle.AllocStrong(managed);

            // The weak GC handle is unused for non-RefCounted objects, and thus it's not allocated.
            if (refCounted)
            {
                if (weakGCHandle.IsAllocated)
                    weakGCHandle.Target = managed;
                else
                    weakGCHandle = CustomGCHandle.AllocWeak(managed);
            }

            NativeFuncs.godotsharp_internal_tie_managed_to_unmanaged_with_pre_setup(
                (IntPtr)strongGCHandle, (IntPtr)weakGCHandle, unmanaged);
        }

        public static GodotObject EngineGetSingleton(string name)
        {
            using godot_string src = Marshaling.ConvertStringToNative(name);
            return UnmanagedGetManaged(NativeFuncs.godotsharp_engine_get_singleton(src));
        }
    }
}
